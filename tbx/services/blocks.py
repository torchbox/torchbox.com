from tbx.core.blocks import StoryBlock
from wagtail import blocks
from wagtail.blocks import CharBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock


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


class PartnersBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255,
    )
    partner_logos = blocks.ListBlock(ImageChooserBlock(), label="Logos")

    class Meta:
        icon = "openquote"
        label = "Partner logos"
        template = "patterns/molecules/streamfield/blocks/partners_block.html"


class ServiceStoryBlock(StoryBlock):
    # Dev note - include work listing and blog listing blocks here when merged
    partners_block = PartnersBlock(
        icon="openquote",
        label="Partners logos",
        template="patterns/molecules/streamfield/blocks/partners_block.html",
    )
    showcase = ShowcaseBlock(
        icon="tasks",
        template="patterns/molecules/streamfield/blocks/showcase_block.html",
    )
