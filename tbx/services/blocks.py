from tbx.core.blocks import (
    BlogChooserBlock,
    FeaturedCaseStudyBlock,
    ShowcaseBlock,
    StoryBlock,
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


class ServiceStoryBlock(StoryBlock):
    partners_block = PartnersBlock()
    showcase = ShowcaseBlock()
    featured_case_study = FeaturedCaseStudyBlock()
    blog_chooser = BlogChooserBlock()
    work_chooser = WorkChooserBlock()
