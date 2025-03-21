from itertools import chain

from django import forms
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.http import urlencode

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.signals import page_published
from wagtail.snippets.models import register_snippet

from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField
from tbx.core.utils.models import (
    ColourThemeMixin,
    ContactMixin,
    NavigationFields,
    SocialFields,
)
from tbx.images.models import CustomImage
from tbx.people.blocks import ContactCTABlock
from tbx.people.forms import ContactAdminForm
from tbx.taxonomy.models import Team


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
    email_text = models.EmailField(
        blank=True,
    )
    cta = StreamField(
        [("call_to_action", ContactCTABlock(label="CTA"))],
        blank=True,
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
            return f"{self.name} – “{self.title}”{default}"
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
        FieldPanel("email_text"),
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


class PersonPage(BasePage):
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

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
        index.SearchField("biography"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("role"),
        FieldPanel("intro"),
        FieldPanel("biography"),
        FieldPanel("image"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + NavigationFields.promote_panels
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
            FieldPanel("related_teams", widget=forms.CheckboxSelectMultiple),
        ]
    )

    def __str__(self) -> str:
        return self.title

    @cached_property
    def teams(self):
        return self.related_teams.all()

    @cached_property
    def author_posts(self):
        # this import is added here in order to avoid circular imports
        from tbx.blog.models import BlogPage

        try:
            author_snippet = Author.objects.get(person_page__pk=self.pk)
        except Author.DoesNotExist:
            return []
        except Author.MultipleObjectsReturned:
            return []

        # Format for template
        return (
            BlogPage.objects.filter(authors__author=author_snippet)
            .live()
            .public()
            .prefetch_related("authors__author")
            .order_by("-date")[:3]
        )

    @cached_property
    def related_works(self):
        """Returns work pages authored by the person, giving preference to Work rather than Historical work pages"""
        # this import is added here in order to avoid circular imports
        from tbx.work.models import HistoricalWorkPage, WorkPage

        # only do this if page has been created
        # otherwise you get misleading results during preview
        # when creating a new page
        if not self.pk:
            return []

        prefetch_listing_images = models.Prefetch(
            "header_image",
            queryset=CustomImage.objects.prefetch_renditions(
                "fill-370x370|format-webp",
                "fill-370x335|format-webp",
                "fill-740x740|format-webp",
                "fill-740x670|format-webp",
            ),
        )

        # Get the latest 3 work pages by this author
        recent_works = (
            WorkPage.objects.filter(authors__author__person_page=self.pk)
            .live()
            .public()
            .defer_streamfields()
            .prefetch_related(prefetch_listing_images)
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
                .defer_streamfields()
                .prefetch_related(prefetch_listing_images)
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
class PersonIndexPage(BasePage):
    strapline = models.CharField(max_length=255)

    template = "patterns/pages/team/team_listing.html"

    subpage_types = ["PersonPage"]

    content_panels = BasePage.content_panels + [
        FieldPanel("strapline"),
    ]

    def __str__(self) -> str:
        return self.title

    @cached_property
    def people(self):
        prefetch_images = models.Prefetch(
            "image",
            queryset=CustomImage.objects.prefetch_renditions(
                "fill-230x230|format-webp", "fill-370x370|format-webp"
            ),
        )
        return (
            PersonPage.objects.child_of(self)
            .order_by("title")
            .live()
            .public()
            .prefetch_related(prefetch_images)
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

        # use page to filter
        page = request.GET.get("page", 1)

        # Pagination
        paginator = Paginator(people, 20)  # Show 20 people per page

        people = paginator.get_page(page)

        tags = Team.objects.all()

        context.update(
            people=people,
            tags=tags,
            extra_url_params=urlencode(extra_url_params),
        )
        return context


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

    def __str__(self) -> str:
        return self.name

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
