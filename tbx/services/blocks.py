from tbx.core.blocks import (
    BlogChooserBlock,
    EventBlock,
    FeaturedCaseStudyBlock,
    FourPhotoCollageBlock,
    IconKeyPointsBlock,
    ImageWithAltTextBlock,
    PartnersBlock,
    PhotoCollageBlock,
    PromoBlock,
    ShowcaseBlock,
    StoryBlock,
    TabbedParagraphBlock,
    WorkChooserBlock,
)
from wagtail import blocks


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
        group = "Custom"


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
    # redefine the heading 2 block from StoryBlock and use the motif heading template
    h2 = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading2_motif_block.html",
        group="Basics",
    )
    # redefine the paragraph block from StoryBlock to exclude the h2 option
    paragraph = blocks.RichTextBlock(
        icon="pilcrow",
        template="patterns/molecules/streamfield/blocks/paragraph_block.html",
        features=["h3", "h4", "bold", "italic", "ul", "ol", "link", "document-link"],
        group="Basics",
    )


class ServiceAreaStoryBlock(StoryBlock):
    blog_chooser = BlogChooserBlock()
    four_photo_collage = FourPhotoCollageBlock()
    key_points = IconKeyPointsBlock(label="Key points with icons")
    work_chooser = WorkChooserBlock()
