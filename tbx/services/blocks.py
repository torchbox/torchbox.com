from django.utils.functional import cached_property

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


class CaseStudyStructValue(blocks.StructValue):
    @cached_property
    def featured_case_study_image(self):
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


class ServiceStoryBlock(StoryBlock):
    partners_block = PartnersBlock(
        icon="openquote",
        label="Partners logos",
        template="patterns/molecules/streamfield/blocks/partners_block.html",
    )
    showcase = ShowcaseBlock(
        icon="tasks",
        template="patterns/molecules/streamfield/blocks/showcase_block.html",
    )
    featured_case_study = FeaturedCaseStudyBlock(
        template="patterns/molecules/streamfield/blocks/featured_case_study.html",
    )
