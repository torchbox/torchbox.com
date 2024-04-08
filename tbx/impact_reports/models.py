from django.db import models
from django.utils.text import slugify

from tbx.core.utils.fields import StreamField
from tbx.impact_reports.blocks import ImpactReportStoryBlock
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    TitleFieldPanel,
)
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index


class ImpactReportPage(Page):
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

    body = StreamField(ImpactReportStoryBlock(), use_json_field=True)

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

    search_fields = Page.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]

    @property
    def headings(self):
        """
        Gets all of the impact report headers' short headings and their slugs,
        including the Introduction.

        This is used to create a table-of-contents like section at the top of
        the page where viewers can jump to the top of each impact report heading
        and Introduction.
        """

        headings = [
            {
                "short_heading": self.introduction_title,
                "slug": slugify(self.introduction_title),
            },
        ]

        for block in self.body:
            if block.block_type == "impact_report_heading":
                headings.append(
                    {
                        "short_heading": block.value["short_heading"],
                        "slug": slugify(block.value["short_heading"]),
                    }
                )

        return headings
