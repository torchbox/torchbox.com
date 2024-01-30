from django.utils.safestring import mark_safe

from tbx.core.blocks import StoryBlock
from wagtail import blocks


class NumericStatisticsBlock(blocks.StructBlock):
    headline_number = blocks.CharBlock(
        max_length=255,
        help_text=mark_safe("A numerical value e.g. <strong>30%</strong>"),
    )
    description = blocks.TextBlock(
        help_text=mark_safe(
            "Text to describe the change e.g. <strong>Reduction in accessibility errors</strong>"
        )
    )
    further_details = blocks.TextBlock(
        required=False,
        help_text=mark_safe(
            "Text to give more information, e.g. <strong>Over 80% of pages</strong>"
        ),
    )

    class Meta:
        icon = "table"


class TextualStatisticsBlock(blocks.StructBlock):
    headline_text = blocks.CharBlock(
        max_length=255,
        help_text=mark_safe(
            "Describe a general improvement, e.g. <strong>Reduction in accessibility issues</strong>"
        ),
    )
    further_details = blocks.TextBlock(
        required=False,
        help_text=mark_safe(
            "Text to give more information, e.g. <strong>Over 80% of pages</strong>"
        ),
    )

    class Meta:
        icon = "info-circle"


class WorkSectionContent(StoryBlock):
    numeric_stats = blocks.ListBlock(
        NumericStatisticsBlock,
        group="Results",
        max_num=3,
        template="patterns/molecules/streamfield/blocks/stats_numeric.html",
    )
    textual_stats = blocks.ListBlock(
        TextualStatisticsBlock,
        group="Results",
        max_num=2,
        template="patterns/molecules/streamfield/blocks/stats_textual.html",
    )


class SectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=255)
    content = WorkSectionContent()

    class Meta:
        icon = "media"
        template = "patterns/molecules/streamfield/blocks/work_section_block.html"


class WorkStoryBlock(blocks.StreamBlock):
    section = SectionBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
