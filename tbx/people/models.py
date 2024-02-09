from itertools import chain

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.http import urlencode

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from phonenumber_field.modelfields import PhoneNumberField
from tbx.blog.models import BlogPage
from tbx.core.utils.models import ColourThemeMixin, SocialFields
from tbx.people.forms import ContactForm
from tbx.taxonomy.models import Team
from tbx.work.models import HistoricalWorkPage, WorkIndexPage, WorkPage
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.signals import page_published
from wagtail.snippets.models import register_snippet


class PersonPage(ColourThemeMixin, SocialFields, Page):
    template = "patterns/pages/team/team_detail.html"

    parent_page_types = ["PersonIndexPage"]

    role = models.CharField(max_length=255, blank=True)
    intro = RichTextField(blank=True)
    biography = RichTextField(blank=True)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    related_teams = ParentalManyToManyField(
        "taxonomy.Team", related_name="people_pages"
    )

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
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
            FieldPanel("related_teams", widget=forms.CheckboxSelectMultiple),
        ]
    )

    @cached_property
    def author_posts(self):
        # Get the BlogPages associated with this page's authors
        blog_pages = (
            BlogPage.objects.live().filter(authors__page=self).order_by("-date")
        )

        # Format for template
        return [
            {
                "title": blog_post.title,
                "url": blog_post.url,
                "author": blog_post.first_author,
                "date": blog_post.date,
                "tags": blog_post.related_teams,
            }
            for blog_post in blog_pages
        ]

    @cached_property
    def related_works(self):
        """Returns work pages authored by the person, giving preference to Work rather than Historical work pages"""
        # Get the latest 3 work pages by this author
        recent_works = (
            WorkPage.objects.filter(authors__author__person_page=self.pk)
            .live()
            .public()
            .distinct()
            .order_by("-date")[:3]
        )

        remaining_slots = 3 - len(recent_works)

        if remaining_slots > 0:
            # Get the latest 3 historical work pages by this author iff necessary
            historical_works = (
                HistoricalWorkPage.objects.filter(authors__author__person_page=self.pk)
                .live()
                .public()
                .distinct()
                .order_by("-date")[:remaining_slots]
            )

        # Combine the two querysets and get the first three results
        works = list(chain(historical_works, recent_works))[:3]
        return works

    @cached_property
    def work_index(self):
        return WorkIndexPage.objects.live().public().first()


# Person index
class PersonIndexPage(ColourThemeMixin, SocialFields, Page):
    strapline = models.CharField(max_length=255)

    template = "patterns/pages/team/team_listing.html"

    subpage_types = ["PersonPage"]

    @cached_property
    def people(self):
        return PersonPage.objects.order_by("title").live().public()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get people_pages
        people_pages = self.people

        # Filter by related_team slug
        slug_filter = request.GET.get("filter")
        extra_url_params = {}

        if slug_filter:
            people_pages = people_pages.filter(related_teams__slug=slug_filter)
            extra_url_params["filter"] = slug_filter

        # format for template
        people_pages = [
            {
                "title": people_page.title,
                "url": people_page.url,
                "type": people_page.role,
                "tags": people_page.related_teams,
            }
            for people_page in people_pages
        ]

        tags = Team.objects.all()

        context.update(
            people_pages=people_pages,
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


@register_snippet
class Contact(index.Indexed, models.Model):
    name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    email_address = models.EmailField()
    phone_number = PhoneNumberField(blank=True, null=True)
    default_contact = models.BooleanField(default=False, blank=True, null=True)
    base_form_class = ContactForm

    def __str__(self):
        return self.name

    search_fields = [
        index.AutocompleteField("name"),
        index.SearchField("name"),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("default_contact", widget=forms.CheckboxInput),
        FieldPanel("image"),
        FieldPanel("email_address"),
        FieldPanel("phone_number"),
    ]


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
