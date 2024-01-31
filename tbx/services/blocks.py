from django.utils.functional import cached_property

from tbx.core.blocks import StoryBlock
from wagtail import blocks
from wagtail.blocks import CharBlock, PageChooserBlock, StructBlock
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


class CaseStudyStructValue(blocks.StructValue):
    @cached_property
    def featured_case_study_image(self):
        """
        Retrieve the main image for a featured case study.

        This property attempts to fetch the main image associated with the current object.
        If the object has a direct 'image' attribute, it returns that image.
        If the object has a 'link' attribute, it checks the linked page's content type
        and returns the corresponding image:
            - If the linked page is a 'WorkPage', it returns the `header_image`.
            - If the linked page is a 'HistoricalWorkPage', it returns the `feed_image`.

        If no suitable image is found, it returns None.
        """
        if image := self.get("image"):
            return image
        elif page := self.get("link"):
            model = page.content_type.model_class().__name__
            if model == "WorkPage":
                return page.specific.header_image
            elif model == "HistoricalWorkPage":
                return page.specific.feed_image
        return None

    @cached_property
    def featured_case_study_logo(self):
        """
        Retrieve the logo for a featured case study.

        This property attempts to fetch the logo associated with the current object.
        If the object has a direct 'logo' attribute, it returns that logo.
        If the object has a 'link' attribute and the linked page is of type 'WorkPage',
        it returns the logo from that page.

        If no suitable logo is found, it returns None.
        """
        if logo := self.get("logo"):
            return logo
        elif page := self.get("link"):
            if page.content_type.model_class().__name__ == "WorkPage":
                return page.specific.logo
        return None


class FeaturedCaseStudyBlock(blocks.StructBlock):
    link = blocks.PageChooserBlock(
        page_type=["work.WorkPage", "work.HistoricalWorkPage"]
    )
    tagline = blocks.CharBlock(max_length=255)
    text = blocks.RichTextBlock(required=False)
    image = ImageChooserBlock(required=False)
    logo = ImageChooserBlock(required=False)

    class Meta:
        icon = "bars"
        value_class = CaseStudyStructValue
        template = "patterns/molecules/streamfield/blocks/featured_case_study.html",


class BlogChooserBlock(blocks.StructBlock):
    featured_blog_heading = CharBlock(max_length=255)
    blog_pages = blocks.ListBlock(
        PageChooserBlock(page_type="blog.BlogPage"),
        min_num=1,
        max_num=3,
    )

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/blog_chooser_block.html"


class WorkChooserBlock(blocks.StructBlock):
    featured_work_heading = CharBlock(max_length=255)
    work_pages = blocks.ListBlock(
        PageChooserBlock(page_type=["work.WorkPage", "work.HistoricalWorkPage"]),
        min_num=1,
        max_num=3,
    )

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/work_chooser_block.html"


class ServiceStoryBlock(StoryBlock):
    partners_block = PartnersBlock()
    showcase = ShowcaseBlock()
    featured_case_study = FeaturedCaseStudyBlock()
    blog_chooser = BlogChooserBlock()
    work_chooser = WorkChooserBlock()
