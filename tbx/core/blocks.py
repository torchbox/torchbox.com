from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.functional import cached_property

from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail_webstories.blocks import (
    ExternalStoryEmbedBlock as WebstoryExternalStoryEmbedBlock,
)
from wagtailmarkdown.blocks import MarkdownBlock
from wagtailmedia.blocks import VideoChooserBlock


class LinkStructValue(blocks.StructValue):
    @cached_property
    def url(self):
        if page := self.get("page"):
            return page.get_url()
        elif link_url := self.get("link_url"):
            return link_url

    @cached_property
    def text(self):
        if link_text := self.get("link_text"):
            return link_text
        elif page := self.get("page"):
            return page.title


class InternalLinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    link_text = blocks.CharBlock(required=False)

    class Meta:
        label = "Internal link"
        icon = "link"
        value_class = LinkStructValue


class ExternalLinkBlock(blocks.StructBlock):
    link_url = blocks.URLBlock(label="URL")
    link_text = blocks.CharBlock()

    class Meta:
        label = "External link"
        icon = "link"
        value_class = LinkStructValue


class LinkBlock(blocks.StreamBlock):
    internal_link = InternalLinkBlock()
    external_link = ExternalLinkBlock()

    class Meta:
        label = "Link"
        icon = "link"
        max_num = 1


class ImageFormatChoiceBlock(blocks.FieldBlock):
    """
    This block is no longer in use. However, because several migrations
    make explicit references to the block class, we cannot remove it
    without breaking the migrations.
    See https://github.com/wagtail/wagtail/issues/3710 for more details.
    """

    pass


class AltTextStructValue(blocks.StructValue):
    def image_alt_text(self):
        if custom_alt_text := self.get("alt_text"):
            return custom_alt_text
        return self.get("image").title


class ImageWithAltTextBlock(blocks.StructBlock):
    """
    Allows for specifying optional alt text for an image.
    """

    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(
        required=False,
        help_text="By default the image title (shown above) is used as the alt text. "
        "Use this field to provide more specific alt text if required.",
    )

    class Meta:
        icon = "image"
        value_class = AltTextStructValue


class ImageBlock(ImageWithAltTextBlock):
    """
    In addition to specifying optional alt text for an image, this block allows
    for specifying a caption, attribution and whether the image is decorative.
    """

    image_is_decorative = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="If checked, this will make the alt text empty.",
    )
    caption = blocks.CharBlock(required=False)
    attribution = blocks.CharBlock(required=False)


class ImageWithLinkBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    link = LinkBlock(required=False)

    class Meta:
        icon = "site"


class PullQuoteBlock(blocks.StructBlock):
    quote = blocks.CharBlock(form_classname="quote title")
    attribution = blocks.CharBlock()
    role = blocks.CharBlock(required=False)
    logo = ImageChooserBlock(
        required=False,
        help_text="You may optionally add either a company logo or author image",
    )
    author_image = ImageChooserBlock(
        required=False,
        help_text="You may optionally add either a company logo or author image",
    )
    call_to_action = LinkBlock(required=False)

    def clean(self, value):
        result = super().clean(value)
        if value["logo"] and value["author_image"]:
            raise StructBlockValidationError(
                block_errors={
                    "author_image": ValidationError(
                        "You must specify either an author image or a company logo, not both."
                    ),
                    "logo": ValidationError(
                        "You must specify either an author image or a company logo, not both."
                    ),
                }
            )
        return result

    class Meta:
        icon = "openquote"


class VideoBlock(blocks.StructBlock):
    video = VideoChooserBlock()
    # setting autoplay to True adds 'autoplay', 'loop' & 'muted' attrs to video element
    autoplay = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Automatically start and loop the video. Please use sparingly.",
    )
    use_original_width = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Use the original width of the video instead of the default content width. "
        "Note that videos wider than the content width will be limited to the content width.",
    )

    class Meta:
        icon = "media"
        template = "patterns/molecules/streamfield/blocks/video_block.html"


class ButtonLinkStructValue(blocks.StructValue):
    # return an href-ready value for button_link
    def get_button_link(self):
        block = self.get("button_link")[0]
        if (block_type := block.block_type) == "internal_link":
            # Ensure page exists and is live.
            if block.value and block.value.live:
                return block.value.url
        elif block_type == "external_link":
            return block.value
        elif block_type == "email":
            return f"mailto:{block.value}"

        return ""


class CallToActionBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, max_length=255)
    button_text = blocks.CharBlock(max_length=55)
    button_link = blocks.StreamBlock(
        [
            ("internal_link", blocks.PageChooserBlock()),
            ("external_link", blocks.URLBlock()),
            ("email", blocks.EmailBlock()),
        ],
        required=True,
        max_num=1,
    )

    class Meta:
        template = "patterns/molecules/streamfield/blocks/call_to_action.html"
        value_class = ButtonLinkStructValue


class ContactCTABlock(blocks.StructBlock):
    call_to_action = blocks.StreamBlock(
        [("call_to_action", CallToActionBlock())], max_num=1
    )
    person = SnippetChooserBlock("people.Author")

    class Meta:
        template = "patterns/molecules/streamfield/blocks/contact_call_to_action.html"


class ExternalStoryEmbedBlock(WebstoryExternalStoryEmbedBlock):
    """
    This code is no longer in use, unfortunately tbx/core/0001 migration (L407)
    depends explicitly on it & migrations cannot be simply squashed to get around this
    See https://github.com/wagtail/wagtail/issues/3710 for a discussion of a similar issue
    """

    pass


class ShowcaseBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
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
        template = ("patterns/molecules/streamfield/blocks/featured_case_study.html",)


class BlogChooserBlock(blocks.StructBlock):
    featured_blog_heading = blocks.CharBlock(max_length=255)
    blog_pages = blocks.ListBlock(
        blocks.PageChooserBlock(page_type="blog.BlogPage"),
        min_num=1,
        max_num=3,
    )

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/blog_chooser_block.html"


class WorkChooserBlock(blocks.StructBlock):
    featured_work_heading = blocks.CharBlock(max_length=255)
    work_pages = blocks.ListBlock(
        blocks.PageChooserBlock(page_type=["work.WorkPage", "work.HistoricalWorkPage"]),
        min_num=1,
        max_num=3,
    )

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/work_chooser_block.html"


class PromoBlock(blocks.StructBlock):
    title = blocks.TextBlock()
    description = blocks.TextBlock()
    image = ImageChooserBlock()
    button_text = blocks.CharBlock(max_length=55)
    button_link = blocks.StreamBlock(
        [
            ("internal_link", blocks.PageChooserBlock()),
            ("external_link", blocks.URLBlock()),
            ("email", blocks.EmailBlock()),
        ],
        required=True,
        max_num=1,
    )
    secondary_link = LinkBlock(required=False, label="Secondary link")

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/promo_block.html"
        value_class = ButtonLinkStructValue


class PhotoCollageBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    intro = blocks.TextBlock(label="Introduction")
    page = blocks.PageChooserBlock(required=False, label="Button link")
    link_text = blocks.CharBlock(
        required=False,
        max_length=55,
        label="Button text",
    )
    images = blocks.ListBlock(
        ImageWithAltTextBlock(label="Photo"),
        min_num=6,
        max_num=6,
        label="Photos",
        help_text="Exactly six required.",
        default=[{"image": None, "alt_text": ""}] * 6,
    )

    def clean(self, value):
        struct_value = super().clean(value)

        errors = {}
        page = value.get("page")
        link_text = value.get("link_text")

        if page and not link_text:
            error = ErrorList(
                [ValidationError("You must add link text for the specified page.")]
            )
            errors["link_text"] = error

        if link_text and not page:
            error = ErrorList(
                [
                    ValidationError(
                        "You must specify a page for the link text you have provided."
                    )
                ]
            )
            errors["page"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value

    class Meta:
        icon = "image"
        template = "patterns/molecules/streamfield/blocks/photo_collage_block.html"


class StoryBlock(blocks.StreamBlock):
    h2 = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading2_block.html",
    )
    h3 = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading3_block.html",
    )
    h4 = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading4_block.html",
    )
    intro = blocks.RichTextBlock(
        icon="pilcrow",
        template="patterns/molecules/streamfield/blocks/intro_block.html",
    )
    paragraph = blocks.RichTextBlock(
        icon="pilcrow",
        template="patterns/molecules/streamfield/blocks/paragraph_block.html",
    )
    image = ImageBlock(
        template="patterns/molecules/streamfield/blocks/image_block.html",
    )
    call_to_action = CallToActionBlock(
        label="Call to Action",
        template="patterns/molecules/streamfield/blocks/call_to_action.html",
    )
    contact_call_to_action = ContactCTABlock(
        label="Contact Call to Action",
        template="patterns/molecules/streamfield/blocks/contact_call_to_action.html",
    )
    pullquote = PullQuoteBlock(
        template="patterns/molecules/streamfield/blocks/pullquote_block.html"
    )
    raw_html = blocks.RawHTMLBlock(
        label="Raw HTML",
        icon="code",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )
    mailchimp_form = blocks.RawHTMLBlock(
        label="Mailchimp embedded form",
        icon="code",
        template="patterns/molecules/streamfield/blocks/mailchimp_form_block.html",
    )
    markdown = MarkdownBlock(
        icon="code",
        template="patterns/molecules/streamfield/blocks/markdown_block.html",
    )
    embed = EmbedBlock(
        icon="code",
        template="patterns/molecules/streamfield/blocks/embed_block.html",
        group="Media",
    )
    video_block = VideoBlock(group="Media")

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"


class HomePageStoryBlock(StoryBlock):
    showcase = ShowcaseBlock()
    featured_case_study = FeaturedCaseStudyBlock()
    blog_chooser = BlogChooserBlock()
    work_chooser = WorkChooserBlock()
    photo_collage = PhotoCollageBlock()
    promo = PromoBlock()
