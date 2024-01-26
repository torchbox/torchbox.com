from tbx.core.blocks import StoryBlock
from wagtail import blocks
from wagtail.blocks import CharBlock, StructBlock


class ShowcaseBlock(StructBlock):
    title = CharBlock(max_length=255)
    showcase_paragraphs = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("heading", blocks.CharBlock()),
                ("summary", blocks.RichTextBlock()),
                ("page", blocks.PageChooserBlock(required=False)),
            ],
            help_text="Add a showcase paragraph, with summary text and an optional page link",
            icon="breadcrumb-expand",
        ),
        min_num=2,
        max_num=10,
        help_text="Add at least two showcase paragraphs",
    )

    class Meta:
        icon = "tasks"
        template = "patterns/molecules/streamfield/blocks/showcase_block.html"


class ServiceStoryBlock(StoryBlock):
    # Dev note - include partners_block here when merged,
    showcase = ShowcaseBlock(
        icon="tasks",
        template="patterns/molecules/streamfield/blocks/showcase_block.html",
    )
