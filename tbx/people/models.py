import os
from concurrent.futures import ThreadPoolExecutor
from itertools import chain

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.http import urlencode

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from tbx.core.utils.models import ColourThemeMixin, SocialFields
from tbx.people.blocks import ContactCTABlock
from tbx.people.forms import ContactAdminForm
from tbx.taxonomy.models import Team
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.signals import page_published
from wagtail.snippets.models import register_snippet


@register_snippet
class Contact(index.Indexed, models.Model):
    """
    This is used in the site-wide footer, and can be configured
    on a per-page basis via the `ContactMixin`
    """

    base_form_class = ContactAdminForm

    title = models.CharField(
        max_length=255,
        blank=True,
    )
    text = models.TextField(
        blank=True,
    )
    cta = StreamField(
        [("call_to_action", ContactCTABlock(label="CTA"))],
        blank=True,
        use_json_field=True,
        max_num=1,
    )

    name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    default_contact = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        help_text="Make this the default contact for the site. "
        "Setting this will override any existing default.",
    )

    def __str__(self):
        default = " (default)" if self.default_contact else ""
        if self.title:
            return "{} – “{}”{}".format(self.name, self.title, default)
        return self.name + default

    def save(self, *args, **kwargs):
        # If user wants to enable the default contact option
        if self.default_contact:
            # Make sure only one default contact exists
            self.__class__.objects.filter(default_contact=True).update(
                default_contact=False
            )
        super().save(*args, **kwargs)

    @property
    def link(self):
        if cta := self.cta:
            block = cta[0]
            return block.value.url

        return ""

    @property
    def button_text(self):
        if cta := self.cta:
            block = cta[0]
            return block.value.get("button_text", "Get in touch")

        return ""

    search_fields = [
        index.AutocompleteField("name"),
        index.SearchField("name"),
    ]

    panels = [
        FieldPanel("title"),
        FieldPanel("text"),
        FieldPanel("cta", heading="Call to action"),
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("role"),
                FieldPanel("image"),
                FieldPanel("default_contact", widget=forms.CheckboxInput),
            ],
            "Contact person",
        ),
    ]


class ContactMixin(models.Model):
    """
    Provides a `contact` field so that a page can have its own contact
    in the site-wide footer, instead of the default contact.
    """

    contact = models.ForeignKey(
        "people.Contact",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="The contact will be applied to this page's footer and all of its "
        "descendants.\nIf no contact is selected, it will be derived from "
        "this page's ancestors, eventually falling back to the default contact.",
    )

    promote_panels = [FieldPanel("contact")]

    @cached_property
    def footer_contact(self):
        """
        Use the page's own contact if set, otherwise, derive the contact from
        its ancestors, and finally fall back to the default contact.

        NOTE: if, for some reason, a default contact doesn't exist, this will
        return None, in which case, we'll not display the block in the footer template.
        """
        if contact := self.contact:
            return contact

        ancestors = (
            self.get_ancestors().defer_streamfields().specific().order_by("-depth")
        )
        for ancestor in ancestors:
            if getattr(ancestor, "contact_id", None) is not None:
                return ancestor.contact

        # _in theory_, there should only be one Contact object with default_contact=True.
        # (see `tbx.people.models.Contact.save()`)
        return Contact.objects.filter(default_contact=True).first()

    class Meta:
        abstract = True


class PersonPage(ColourThemeMixin, ContactMixin, SocialFields, Page):
    template = "patterns/pages/team/team_detail.html"

    parent_page_types = ["PersonIndexPage"]

    role = models.CharField(max_length=255)
    intro = RichTextField(blank=True)
    biography = RichTextField()
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    related_teams = ParentalManyToManyField("taxonomy.Team", related_name="people")

    @cached_property
    def teams(self):
        return self.related_teams.all()

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("biography"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("role"),
        FieldPanel("intro"),
        FieldPanel("biography"),
        FieldPanel("image"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
            FieldPanel("related_teams", widget=forms.CheckboxSelectMultiple),
        ]
    )

    @cached_property
    def author_posts(self):
        author_snippet = Author.objects.get(person_page__pk=self.pk)
        # this import is added here in order to avoid circular imports
        from tbx.blog.models import BlogPage

        # Format for template
        return [
            {
                "title": blog_post.title,
                "url": blog_post.url,
                "read_time": blog_post.read_time,
                "date": blog_post.date,
                "tags": blog_post.tags,
            }
            for blog_post in BlogPage.objects.live()
            .filter(authors__author=author_snippet)
            .order_by("-date")[:3]
        ]

    @cached_property
    def related_works(self):
        """Returns work pages authored by the person, giving preference to Work rather than Historical work pages"""
        # this import is added here in order to avoid circular imports
        from tbx.work.models import HistoricalWorkPage, WorkPage

        # Get the latest 3 work pages by this author
        recent_works = (
            WorkPage.objects.filter(authors__author__person_page=self.pk)
            .live()
            .public()
            .distinct()
            .order_by("-date")[:3]
        )

        remaining_slots = 3 - len(recent_works)

        if remaining_slots == 0:
            # No historical works needed, just return recent works
            works = recent_works

        else:
            # Get the latest 3 historical work pages by this author iff necessary
            historical_works = (
                HistoricalWorkPage.objects.filter(authors__author__person_page=self.pk)
                .live()
                .public()
                .distinct()
                .order_by("-date")[:remaining_slots]
            )

            # Combine the two querysets and get the first three results
            works = list(chain(historical_works, recent_works))

        return works

    @cached_property
    def work_index(self):
        # this import is added here in order to avoid circular imports
        from tbx.work.models import WorkIndexPage

        return WorkIndexPage.objects.live().public().first()


# Person index
class PersonIndexPage(ColourThemeMixin, ContactMixin, SocialFields, Page):
    strapline = models.CharField(max_length=255)

    template = "patterns/pages/team/team_listing.html"

    subpage_types = ["PersonPage"]

    @cached_property
    def people(self):
        return (
            PersonPage.objects.child_of(self)
            .order_by("title")
            .live()
            .public()
            .prefetch_related("image")
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get people
        people = self.people

        # Filter by related_team slug
        slug_filter = request.GET.get("filter")
        extra_url_params = {}

        if slug_filter:
            people = people.filter(related_teams__slug=slug_filter)
            extra_url_params["filter"] = slug_filter

        tags = Team.objects.all()

        context.update(
            people=people,
            tags=tags,
            extra_url_params=urlencode(extra_url_params),
        )
        return context

    content_panels = Page.content_panels + [
        FieldPanel("strapline"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )


# An author snippet which keeps a copy of a person's details in case they leave and their page is unpublished
# Could also be used for external authors
@register_snippet
class Author(index.Indexed, models.Model):
    person_page = models.OneToOneField(
        "people.PersonPage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    def update_manual_fields(self, person_page):
        self.name = person_page.title
        self.role = person_page.role
        self.image = person_page.image

    def clean(self):
        if not self.person_page and not self.name:
            raise ValidationError(
                {"person_page": "You must set either 'Person page' or 'Name'"}
            )

        if self.person_page:
            self.update_manual_fields(self.person_page)

    def __str__(self):
        return self.name

    search_fields = [
        index.AutocompleteField("name"),
        index.SearchField("name"),
    ]

    panels = [
        FieldPanel("person_page"),
        MultiFieldPanel(
            [FieldPanel("name"), FieldPanel("role"), FieldPanel("image")],
            "Manual fields",
        ),
    ]


@receiver(page_published, sender=PersonPage)
def update_author_on_page_publish(instance, **kwargs):
    author, created = Author.objects.get_or_create(person_page=instance)
    author.update_manual_fields(instance)
    author.save()


@receiver(page_published, sender=PersonIndexPage)
def update_image_renditions_on_page_publish(instance, **kwargs):
    def image_renditions(person):
        if image := person.image:
            image.get_renditions(
                "format-webp|fill-230x230",
                "format-webp|fill-370x370",
            )

    max_workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(image_renditions, instance.people)


class ContactReason(Orderable):
    page = ParentalKey("people.ContactReasonsList", related_name="reasons")
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)


@register_snippet
class ContactReasonsList(ClusterableModel):
    name = models.CharField(max_length=255, blank=True)
    heading = models.TextField(blank=False)
    is_default = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.name

    panels = [
        FieldPanel("name"),
        FieldPanel("heading"),
        FieldPanel("is_default", widget=forms.CheckboxInput),
        InlinePanel("reasons", label="Reasons", max_num=3),
    ]

    def clean(self):
        if self.is_default:
            qs = ContactReasonsList.objects.filter(is_default=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {"is_default": ["There already is another default snippet."]}
                )
