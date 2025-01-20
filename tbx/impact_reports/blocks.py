from wagtail.blocks import (
    CharBlock,
    ListBlock,
    RichTextBlock,
    StructBlock,
    URLBlock,
)

from tbx.core.blocks import (
    CustomImageChooserBlock,
    NumericStatisticsBlock,
    StoryBlock,
    TextualStatisticsBlock,
)


class ImpactReportHeadingBlock(StructBlock):
    image = CustomImageChooserBlock(
        required=False,
        help_text="Can be omitted for the first heading immediately after the main image",
    )
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
    image = CustomImageChooserBlock()
    title = CharBlock()
    text = RichTextBlock()

    class Meta:
        icon = "image"
        template = (
            "patterns/molecules/streamfield/blocks/small_image_with_text_block.html"
        )


class InstagramGalleryItemBlock(StructBlock):
    image = CustomImageChooserBlock()
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
    numeric_stats = ListBlock(
        NumericStatisticsBlock,
        group="Results",
        max_num=3,
        template="patterns/molecules/streamfield/blocks/stats_numeric.html",
    )
    textual_stats = ListBlock(
        TextualStatisticsBlock,
        group="Results",
        max_num=2,
        template="patterns/molecules/streamfield/blocks/stats_textual.html",
    )
