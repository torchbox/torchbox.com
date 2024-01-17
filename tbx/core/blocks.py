from django.core.exceptions import ValidationError
from django.utils.functional import cached_property

from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    FieldBlock,
    PageChooserBlock,
    RawHTMLBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    StructValue,
    URLBlock,
)
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail_webstories.blocks import (
    ExternalStoryEmbedBlock as WebstoryExternalStoryEmbedBlock,
)
from wagtailmarkdown.blocks import MarkdownBlock
from wagtailmedia.blocks import VideoChooserBlock


class LinkStructValue(StructValue):
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


class InternalLinkBlock(StructBlock):
    page = PageChooserBlock()
    link_text = CharBlock(required=False)

    class Meta:
        label = "Internal link"
        icon = "link"
        value_class = LinkStructValue


class ExternalLinkBlock(StructBlock):
    link_url = URLBlock(label="URL")
    link_text = CharBlock()

    class Meta:
        label = "External link"
        icon = "link"
        value_class = LinkStructValue


class LinkBlock(StreamBlock):
    internal_link = InternalLinkBlock()
    external_link = ExternalLinkBlock()

    class Meta:
        label = "Link"
        icon = "link"
        max_num = 1


class ImageFormatChoiceBlock(FieldBlock):
    """
    This block is no longer in use. However, because several migrations
    make explicit references to the block class, we cannot remove it
    without breaking the migrations.
    See https://github.com/wagtail/wagtail/issues/3710 for more details.
    """

    pass


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    alt_text = CharBlock(required=False)
    image_is_decorative = BooleanBlock(
        required=False,
        default=False,
        help_text="If checked, this will make the alt text empty.",
    )
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    class Meta:
        icon = "image"


class ImageWithLinkBlock(StructBlock):
    image = ImageChooserBlock()
    link = LinkBlock(required=False)

    class Meta:
        icon = "site"


class PullQuoteBlock(StructBlock):
    quote = CharBlock(form_classname="quote title")
    attribution = CharBlock()
    role = CharBlock()
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


class VideoBlock(StructBlock):
    video = VideoChooserBlock()
    # setting autoplay to True adds 'autoplay', 'loop' & 'muted' attrs to video element
    autoplay = BooleanBlock(
        required=False,
        default=False,
        help_text="Automatically start and loop the video. Please use sparingly.",
    )
    use_original_width = BooleanBlock(
        required=False,
        default=False,
        help_text="Use the original width of the video instead of the default content width. "
        "Note that videos wider than the content width will be limited to the content width.",
    )

    class Meta:
        icon = "media"
        template = "patterns/molecules/streamfield/blocks/video_block.html"


class ExternalStoryEmbedBlock(WebstoryExternalStoryEmbedBlock):
    """
    This code is no longer in use, unfortunately tbx/core/0001 migration (L407)
    depends explicitly on it & migrations cannot be simply squashed to get around this
    See https://github.com/wagtail/wagtail/issues/3710 for a discussion of a similar issue
    """

    pass


class StoryBlock(StreamBlock):
    h2 = CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading2_block.html",
    )
    h3 = CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading3_block.html",
    )
    h4 = CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading4_block.html",
    )
    intro = RichTextBlock(
        icon="pilcrow",
        template="patterns/molecules/streamfield/blocks/intro_block.html",
    )
    paragraph = RichTextBlock(
        icon="pilcrow",
        template="patterns/molecules/streamfield/blocks/paragraph_block.html",
    )
    image = ImageBlock(
        template="patterns/molecules/streamfield/blocks/image_block.html",
    )
    pullquote = PullQuoteBlock(
        template="patterns/molecules/streamfield/blocks/pullquote_block.html"
    )
    raw_html = RawHTMLBlock(
        label="Raw HTML",
        icon="code",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
    )
    mailchimp_form = RawHTMLBlock(
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
