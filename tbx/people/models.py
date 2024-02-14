from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from tbx.core.utils.models import ColourThemeMixin, SocialFields
from tbx.people.blocks import ContactCTABlock
from tbx.people.forms import ContactAdminForm
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

        # _in theory_, there should only be one Contact object with default_contact=True.
        # (see `tbx.people.models.Contact.save()`)
        default_contact = Contact.objects.filter(default_contact=True).first()

        try:
            return next(
                p.contact
                for p in self.get_ancestors().specific().order_by("-depth")
                if getattr(p, "contact", None) is not None
            )
        except StopIteration:
            return default_contact

    @cached_property
    def footer_contact_improved(self):
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

    role = models.CharField(max_length=255, blank=True)
    is_senior = models.BooleanField(default=False)
    intro = RichTextField(blank=True)
    biography = RichTextField(blank=True)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("biography"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("role"),
        FieldPanel("is_senior"),
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
        ]
    )

    @cached_property
    def author_posts(self):
        # return the blogs writen by this member
        author_snippet = Author.objects.get(person_page__pk=self.pk)
        # this import is added here in order to avoid circular imports
        from tbx.blog.models import BlogPage

        # format for template
        return [
            {
                "title": blog_post.title,
                "url": blog_post.url,
                "author": blog_post.first_author,
                "date": blog_post.date,
            }
            for blog_post in BlogPage.objects.live()
            .filter(authors__author=author_snippet)
            .order_by("-date")
        ]

    @cached_property
    def related_works(self):
        # this import is added here in order to avoid circular imports
        from tbx.work.models import HistoricalWorkPage

        # Get the latest 2 work pages by this author
        works = (
            HistoricalWorkPage.objects.filter(authors__author__person_page=self.pk)
            .live()
            .public()
            .distinct()
            .order_by("-date")[:2]
        )
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
    def team(self):
        return PersonPage.objects.order_by("-is_senior", "title").live().public()

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
