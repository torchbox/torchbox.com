from wagtail import blocks

from tbx.core.blocks import (
    NumericStatisticsBlock,
    StoryBlock,
    TextualStatisticsBlock,
)


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
