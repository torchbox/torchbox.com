import math
import string

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Case, DateField, F, Q, When
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.http import urlencode

from bs4 import BeautifulSoup
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from tbx.core.blocks import StoryBlock
from tbx.core.utils.models import SocialFields
from tbx.taxonomy.models import Service
from tbx.work.blocks import WorkStoryBlock
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.signals import page_published


class HistoricalWorkPageScreenshot(Orderable):
    page = ParentalKey("work.HistoricalWorkPage", related_name="screenshots")
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("image"),
    ]


class HistoricalWorkPage(SocialFields, Page):
    """
    This represents Work Pages as they were prior to the 2024
    rebuild of the site. It is kept here to display the older
    work pages that were created prior to 2024.
    """

    template = "patterns/pages/work/historical_work_page.html"

    # Prevent this page type from being created in Wagtail Admin
    parent_page_types = []

    date = models.DateField("Post date", blank=True, null=True)
    body = StreamField(StoryBlock(), use_json_field=True)
    body_word_count = models.PositiveIntegerField(null=True, editable=False)
    homepage_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    visit_the_site = models.URLField(blank=True)

    feed_image = models.ForeignKey(
        "images.CustomImage",
        help_text="Image used on listings and social media.",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    listing_summary = models.CharField(max_length=255, blank=True)
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

    @property
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
        # get 4 pages with same services and exclude self page
        works = (
            HistoricalWorkPage.objects.filter(related_services__in=services)
            .live()
            .distinct()
            .order_by("-id")
            .exclude(pk=self.pk)[:4]
        )
        return works

    @property
    def read_time(self):
        if self.body_word_count:
            return math.ceil(self.body_word_count / 275)
        else:
            return "x"

    @property
    def listing_image(self):
        return self.homepage_image

    @property
    def type(self):
        return "CASE STUDY"

    content_panels = Page.content_panels + [
        FieldPanel("client", classname="client"),
        InlinePanel("authors", label="Author", min_num=1),
        FieldPanel("date"),
        FieldPanel("body"),
        FieldPanel("homepage_image"),
        InlinePanel("screenshots", label="Screenshots"),
        FieldPanel("visit_the_site"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        FieldPanel("feed_image"),
        FieldPanel("listing_summary"),
        FieldPanel("related_services", widget=forms.CheckboxSelectMultiple),
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]


class WorkPage(SocialFields, Page):
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

    body = StreamField(WorkStoryBlock(), use_json_field=True)

    listing_summary = models.CharField(max_length=255, blank=True)
    related_services = ParentalManyToManyField(
        "taxonomy.Service", related_name="case_studies"
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

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        FieldPanel("listing_summary"),
        FieldPanel("related_services", widget=forms.CheckboxSelectMultiple),
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]

    @property
    def type(self):
        return "CASE STUDY"

    @cached_property
    def services(self):
        return self.related_services.all()

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
                "related_services": work_page.related_services.all(),
                "listing_image": work_page.header_image,
            }
            # get 3 pages with same services and exclude self page
            for work_page in WorkPage.objects.filter(related_services__in=self.services)
            .live()
            .prefetch_related("related_services", "authors", "authors__author")
            .defer_streamfields()
            .distinct()
            .order_by("-id")
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

    @property
    def work_index(self):
        ancestor = WorkIndexPage.objects.ancestor_of(self).order_by("-depth").first()

        if ancestor:
            return ancestor
        else:
            # No ancestors are work indexes,
            # just return first work index in database
            return WorkIndexPage.objects.live().public().first()


# Work index page
class WorkIndexPage(SocialFields, Page):
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
                "workpage__related_services",
                "historicalworkpage__related_services",
                "authors",
                "authors__author",
            )
            .annotate(
                priority=Case(
                    When(workpage__isnull=False, then=F("workpage__date")),
                    default=F("historicalworkpage__date"),
                    output_field=DateField(),
                )
            )
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
                | Q(historicalworkpage__related_services__slug=slug_filter),
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
                "related_services": work.related_services.all(),
                "read_time": work.read_time,
                "listing_image": getattr(work, "header_image", None)
                or getattr(work, "homepage_image", None),
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

        related_services = Service.objects.all()

        context.update(
            works=works,
            related_services=related_services,
            extra_url_params=urlencode(extra_url_params),
        )

        return context

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]


@receiver(page_published, sender=WorkPage)
@receiver(page_published, sender=HistoricalWorkPage)
def update_body_word_count_on_page_publish(instance, **kwargs):
    instance.set_body_word_count()
    instance.save(update_fields=["body_word_count"])
