import math
import string
from itertools import chain

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Case, DateField, F, Q, When
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.http import urlencode

from bs4 import BeautifulSoup
from modelcluster.fields import ParentalManyToManyField
from tbx.core.blocks import StoryBlock
from tbx.core.utils.fields import StreamField
from tbx.core.utils.models import ColourThemeMixin, SocialFields
from tbx.people.models import ContactMixin
from tbx.taxonomy.models import Sector, Service
from tbx.work.blocks import WorkStoryBlock
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.signals import page_published


class HistoricalWorkPage(ColourThemeMixin, ContactMixin, SocialFields, Page):
    """
    This represents Work Pages as they were prior to the 2024
    rebuild of the site. It is kept here to display the older
    work pages that were created prior to 2024.
    """

    template = "patterns/pages/work/historical_work_page.html"

    # Prevent this page type from being created in Wagtail Admin
    parent_page_types = []

    date = models.DateField("Post date", blank=True, null=True)
    body = StreamField(StoryBlock())
    body_word_count = models.PositiveIntegerField(null=True, editable=False)
    visit_the_site = models.URLField(blank=True)

    # Renamed from feed_image to allow prefetch of field common to WorkPage and
    # HistoricalWorkPage
    header_image = models.ForeignKey(
        "images.CustomImage",
        help_text="Image used on listings and social media.",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Feed image",
    )
    listing_summary = models.CharField(max_length=255, blank=True)
    related_sectors = ParentalManyToManyField(
        "taxonomy.Sector",
        related_name="historical_case_studies",
        blank=True,
    )
    related_services = ParentalManyToManyField(
        "taxonomy.Service", related_name="historical_case_studies"
    )
    client = models.TextField(blank=True)

    # We are setting `db_index=False` on the social_image, otherwise
    # we encounter migration errors on the New Work Page.
    # See Django bug: <https://code.djangoproject.com/ticket/23577>
    social_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        db_index=False,
    )

    def set_body_word_count(self):
        body_basic_html = self.body.stream_block.render_basic(self.body)
        body_text = BeautifulSoup(body_basic_html, "html.parser").get_text()
        remove_chars = string.punctuation + "“”’"
        body_words = body_text.translate(
            body_text.maketrans(dict.fromkeys(remove_chars))
        ).split()
        self.body_word_count = len(body_words)

    @cached_property
    def work_index(self):
        ancestor = WorkIndexPage.objects.ancestor_of(self).order_by("-depth").first()

        if ancestor:
            return ancestor
        else:
            # No ancestors are work indexes,
            # just return first work index in database
            return WorkIndexPage.objects.live().public().first()

    @property
    def first_author(self):
        """Safely return the first author if one exists."""
        author = self.authors.first()
        if author:
            return author.author
        return None

    @property
    def related_works(self):
        services = self.related_services.all()
        sectors = self.related_sectors.all()
        # get 4 pages with same services and exclude self page
        works = (
            HistoricalWorkPage.objects.filter(
                Q(related_sectors__in=sectors) | Q(related_services__in=services)
            )
            .live()
            .distinct()
            .order_by(F("date").desc(nulls_last=True))
            .exclude(pk=self.pk)[:4]
        )
        return works

    @cached_property
    def sectors(self):
        return self.related_sectors.all()

    @cached_property
    def services(self):
        return self.related_services.all()

    @property
    def tags(self):
        return chain(self.services, self.sectors)

    @property
    def read_time(self):
        if self.body_word_count:
            return math.ceil(self.body_word_count / 275)
        else:
            return "x"

    @property
    def listing_image(self):
        return self.header_image

    @property
    def type(self):
        return "CASE STUDY"

    content_panels = Page.content_panels + [
        FieldPanel("client", classname="client"),
        InlinePanel("authors", label="Author", min_num=1),
        FieldPanel("date"),
        FieldPanel("body"),
        FieldPanel("visit_the_site"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            FieldPanel("header_image"),
            FieldPanel("listing_summary"),
            FieldPanel("related_sectors", widget=forms.CheckboxSelectMultiple),
            FieldPanel("related_services", widget=forms.CheckboxSelectMultiple),
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )


class WorkPage(ColourThemeMixin, ContactMixin, SocialFields, Page):
    template = "patterns/pages/work/work_page.html"
    parent_page_types = ["WorkIndexPage"]

    intro = RichTextField(blank=True)
    logo = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    client = models.CharField(max_length=255)
    date = models.DateField("post date", blank=True, null=True)
    body_word_count = models.PositiveIntegerField(null=True, editable=False)

    header_image = models.ForeignKey(
        "images.CustomImage",
        verbose_name="Image",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    header_caption = models.CharField("caption", max_length=255, blank=True)
    header_attribution = models.CharField("attribution", max_length=255, blank=True)

    body = StreamField(WorkStoryBlock())

    listing_summary = models.CharField(max_length=255, blank=True)
    related_services = ParentalManyToManyField(
        "taxonomy.Service", related_name="case_studies"
    )
    related_sectors = ParentalManyToManyField(
        "taxonomy.Sector",
        related_name="case_studies",
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        InlinePanel("authors", label="Author", min_num=1),
        FieldPanel("logo"),
        FieldPanel("client", classname="client"),
        FieldPanel("date"),
        MultiFieldPanel(
            [
                FieldPanel("header_image"),
                FieldPanel("header_caption"),
                FieldPanel("header_attribution"),
            ],
            heading="Header image",
        ),
        FieldPanel("body"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            FieldPanel("listing_summary"),
            MultiFieldPanel(
                [
                    FieldPanel("related_sectors", widget=forms.CheckboxSelectMultiple),
                    FieldPanel("related_services", widget=forms.CheckboxSelectMultiple),
                ],
                heading="Taxonomies",
            ),
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )

    @property
    def type(self):
        return "CASE STUDY"

    @cached_property
    def sectors(self):
        return self.related_sectors.all()

    @cached_property
    def services(self):
        return self.related_services.all()

    @property
    def tags(self):
        return chain(self.services, self.sectors)

    @cached_property
    def first_author(self):
        """Safely return the first author if one exists."""
        if author := self.authors.first():
            return author.author
        return None

    @property
    def related_works(self):
        return [
            {
                "client": work_page.client,
                "title": work_page.title,
                "url": work_page.url,
                "author": work_page.first_author,
                "date": work_page.date,
                "read_time": work_page.read_time,
                "related_sectors": work_page.related_sectors.all(),
                "related_services": work_page.related_services.all(),
                "tags": work_page.tags,
                "listing_image": work_page.header_image,
            }
            # get 3 pages with same services and exclude self page
            for work_page in WorkPage.objects.filter(
                Q(related_sectors__in=self.sectors)
                | Q(related_services__in=self.services)
            )
            .live()
            .prefetch_related(
                "related_sectors", "related_services", "authors", "authors__author"
            )
            .defer_streamfields()
            .distinct()
            .order_by(F("date").desc(nulls_last=True))
            .exclude(pk=self.pk)[:3]
        ]

    def set_body_word_count(self):
        body_basic_html = self.body.stream_block.render_basic(self.body)
        body_text = BeautifulSoup(body_basic_html, "html.parser").get_text()
        remove_chars = string.punctuation + "“”’"
        body_words = body_text.translate(
            body_text.maketrans(dict.fromkeys(remove_chars))
        ).split()
        self.body_word_count = len(body_words)

    @property
    def read_time(self):
        if self.body_word_count:
            return math.ceil(self.body_word_count / 275)
        else:
            return "x"

    @property
    def listing_image(self):
        return self.header_image

    @cached_property
    def work_index(self):
        ancestor = WorkIndexPage.objects.ancestor_of(self).order_by("-depth").first()

        if ancestor:
            return ancestor
        else:
            # No ancestors are work indexes,
            # just return first work index in database
            return WorkIndexPage.objects.live().public().first()


# Work index page
class WorkIndexPage(ColourThemeMixin, ContactMixin, SocialFields, Page):
    template = "patterns/pages/work/work_index_page.html"

    subpage_types = ["HistoricalWorkPage", "WorkPage"]

    @cached_property
    def works(self):
        pages = (
            self.get_children()
            .live()
            .type(HistoricalWorkPage, WorkPage)
            .specific()
            .prefetch_related(
                "workpage",
                "historicalworkpage",
                "workpage__related_sectors",
                "workpage__related_services",
                "historicalworkpage__related_services",
                "authors",
                "authors__author",
                "header_image",
            )
            .annotate(
                priority=Case(
                    When(workpage__isnull=False, then=F("workpage__date")),
                    default=F("historicalworkpage__date"),
                    output_field=DateField(),
                )
            )
            .distinct()
            .order_by(
                "-priority",
                "-pk",
            )
        )
        return pages

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get work pages
        works = self.works

        # for pagination
        extra_url_params = {}

        # Filter by related_service slug
        if slug_filter := request.GET.get("filter"):
            works = works.filter(
                Q(workpage__related_services__slug=slug_filter)
                | Q(historicalworkpage__related_services__slug=slug_filter)
                | Q(workpage__related_sectors__slug=slug_filter)
                | Q(historicalworkpage__related_sectors__slug=slug_filter),
            )
            extra_url_params["filter"] = slug_filter

        # format for template
        works = [
            {
                "title": work.title,
                "client": work.client,
                "url": work.url,
                "author": work.first_author,
                "date": work.date,
                "tags": work.tags,
                "read_time": work.read_time,
                "listing_image": work.listing_image,
            }
            for work in works
        ]

        # use page to filter
        page = request.GET.get("page", 1)

        # Pagination
        paginator = Paginator(works, 10)  # Show 10 works per page

        try:
            works = paginator.page(page)
        except PageNotAnInteger:
            works = paginator.page(1)
        except EmptyPage:
            works = paginator.page(paginator.num_pages)

        # Only show Sectors and Services that have been used
        related_sectors = Sector.objects.filter(
            pk__in=models.Subquery(self.works.values("workpage__related_sectors"))
        )
        related_services = Service.objects.filter(
            Q(pk__in=models.Subquery(self.works.values("workpage__related_services")))
            | Q(
                pk__in=models.Subquery(
                    self.works.values("historicalworkpage__related_services")
                )
            )
        )

        # Used for the purposes of defining the filterable tags
        tags = chain(related_services, related_sectors)

        context.update(
            works=works,
            tags=tags,
            extra_url_params=urlencode(extra_url_params),
        )

        return context

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


@receiver(page_published, sender=WorkPage)
@receiver(page_published, sender=HistoricalWorkPage)
def update_body_word_count_on_page_publish(instance, **kwargs):
    instance.set_body_word_count()
    instance.save(update_fields=["body_word_count"])
