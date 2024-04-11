from tbx.core.blocks import StoryBlock
from wagtail.blocks import (
    CharBlock,
    ListBlock,
    RichTextBlock,
    StructBlock,
    URLBlock,
)
from wagtail.images.blocks import ImageChooserBlock


class ImpactReportHeadingBlock(StructBlock):
    image = ImageChooserBlock(required=True)
    short_heading = CharBlock(
        required=False, help_text="Used for the Table of Contents"
    )
    heading = CharBlock(required=False)

    class Meta:
        icon = "title"
        template = (
            "patterns/molecules/streamfield/blocks/impact_report_heading_block.html"
        )


class SmallImageWithTextBlock(StructBlock):
    image = ImageChooserBlock()
    title = CharBlock()
    text = RichTextBlock()

    class Meta:
        icon = "image"
        template = (
            "patterns/molecules/streamfield/blocks/small_image_with_text_block.html"
        )


class InstagramGalleryItemBlock(StructBlock):
    image = ImageChooserBlock()
    link = URLBlock(
        required=False,
    )

    class Meta:
        icon = "image"


class InstagramGalleryGridBlock(StructBlock):
    items = ListBlock(InstagramGalleryItemBlock())

    class Meta:
        icon = "group"
        template = "patterns/molecules/streamfield/blocks/instagram_gallery_block.html"


class ImpactReportStoryBlock(StoryBlock):
    impact_report_heading = ImpactReportHeadingBlock(group="Impact Report")
    small_image_with_text = SmallImageWithTextBlock(group="Impact Report")
    instagram_gallery = InstagramGalleryGridBlock(group="Impact Report")
