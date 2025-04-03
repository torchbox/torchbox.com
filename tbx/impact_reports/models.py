from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify

from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    TitleFieldPanel,
)
from wagtail.search import index

from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField
from tbx.impact_reports.blocks import ImpactReportStoryBlock


class ImpactReportPage(BasePage):
    template = "patterns/pages/impact_reports/impact_report_page.html"

    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This is for the illustration only. Use an image with dimensions of 571x700",
    )

    hero_caption = models.CharField("caption", max_length=255, blank=True)
    hero_attribution = models.CharField("attribution", max_length=255, blank=True)

    body = StreamField(ImpactReportStoryBlock())

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel("title"),
                FieldPanel("hero_image"),
                FieldPanel("hero_caption"),
                FieldPanel("hero_attribution"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                InlinePanel("authors", label="Author", min_num=1),
            ],
            heading="Introduction",
        ),
        FieldPanel("body"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]

    @property
    def headings(self):
        """
        Gets all of the impact report headers' short headings and their slugs,
        including the Introduction.

        This is used to create a table-of-contents like section at the top of
        the page where viewers can jump to the top of each impact report heading.
        """

        headings = []

        for block in self.body:
            if block.block_type == "impact_report_heading":
                headings.append(
                    {
                        "short_heading": block.value["short_heading"],
                        "slug": slugify(block.value["short_heading"]),
                    }
                )
        return headings

    @cached_property
    def first_author(self):
        """Safely return the first author if one exists."""
        if author := self.authors.first():
            return author.author
        return None
