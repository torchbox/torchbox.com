from tbx.core.blocks import StoryBlock
from wagtail import blocks


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
