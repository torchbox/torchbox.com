from tbx.core.blocks import StoryBlock
from wagtail import blocks


class NumericStatisticsBlock(blocks.StructBlock):
    class Meta:
        icon = "table"
        template = "patterns/molecules/streamfield/blocks/stats_numeric.html"


class TextualStatisticsBlock(blocks.StructBlock):
    class Meta:
        icon = "info-circle"
        template = "patterns/molecules/streamfield/blocks/stats_textual.html"


class WorkSectionContent(StoryBlock):
    # TODO: add stats block here, and any other StreamField blocks specific to WorkPage
    pass


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
