from tbx.core.blocks import (
    BlogChooserBlock,
    EventBlock,
    FeaturedCaseStudyBlock,
    ImageWithAltTextBlock,
    PhotoCollageBlock,
    PromoBlock,
    ShowcaseBlock,
    StoryBlock,
    TabbedParagraphBlock,
    WorkChooserBlock,
)
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class PartnersBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=255,
    )
    partner_logos = blocks.ListBlock(ImageChooserBlock(), label="Logos")

    class Meta:
        icon = "openquote"
        label = "Partner logos"
        template = "patterns/molecules/streamfield/blocks/partners_block.html"


class ValuesBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    intro = blocks.TextBlock(label="Introduction")
    values = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("strapline", blocks.CharBlock(required=False)),
                ("title", blocks.CharBlock()),
                ("text", blocks.RichTextBlock(features=["bold", "italic", "ul"])),
                ("image", ImageWithAltTextBlock()),
            ],
            icon="pick",
        ),
        min_num=1,
        help_text="Add at least one value",
    )

    class Meta:
        icon = "pick"
        label = "Values"
        template = "patterns/molecules/streamfield/blocks/values_block.html"


class ServiceStoryBlock(StoryBlock):
    partners_block = PartnersBlock()
    showcase = ShowcaseBlock()
    featured_case_study = FeaturedCaseStudyBlock()
    blog_chooser = BlogChooserBlock()
    work_chooser = WorkChooserBlock()
    photo_collage = PhotoCollageBlock()
    promo = PromoBlock()
    tabbed_paragraph = TabbedParagraphBlock()
    event = EventBlock()
    values = ValuesBlock()
