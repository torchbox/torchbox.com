import logging
from collections import defaultdict

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.embeds.blocks import EmbedBlock as WagtailEmbedBlock
from wagtail.embeds.embeds import get_embed
from wagtail.embeds.exceptions import EmbedException
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailmarkdown.blocks import MarkdownBlock
from wagtailmedia.blocks import VideoChooserBlock

logger = logging.getLogger(__name__)


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
    for specifying a caption, attribution, whether the image is decorative, and
    whether to remove the desaturation filter.
    """

    remove_desaturation_filter = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Do not apply a desaturation filter to the image.",
    )
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
        group = "Media and images"


class ButtonLinkStructValue(blocks.StructValue):
    def get_button_link_block(self):
        return self.get("button_link")[0]

    # return an href-ready value for button_link
    def get_button_link(self):
        block = self.get_button_link_block()
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
        group = "Custom"


class CaseStudyStructValue(blocks.StructValue):
    @cached_property
    def featured_case_study_image(self):
        """
        Retrieve the main image for a featured case study.
        This property attempts to fetch the main image associated with the current object.
        - If the object has a direct 'image' attribute, it returns that image.
        - If the object has a 'link' attribute, it returns the specific pages
          ('WorkPage' or 'HistoricalWorkPage') corresponding `header_image`.
        - If no suitable image is found, it returns None.
        """
        if image := self.get("image"):
            return image
        elif page := self.get("link"):
            return page.specific.header_image
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


class NumericResultBlock(blocks.StructBlock):
    label = blocks.CharBlock(
        max_length=255,
        help_text=mark_safe(
            "Short text to describe the change e.g. <strong>Raised over</strong>"
        ),
    )
    headline_number = blocks.CharBlock(
        max_length=255,
        help_text=mark_safe("A numerical value e.g. <strong>£600k</strong>"),
    )


class FeaturedCaseStudyBlock(blocks.StructBlock):
    link = blocks.PageChooserBlock(
        page_type=["work.WorkPage", "work.HistoricalWorkPage"]
    )
    numeric_results = blocks.ListBlock(
        NumericResultBlock,
        default=[],  # Do not show pre-populated with 1 item by default.
        group="Results",
        max_num=3,
        required=False,
        template="patterns/molecules/streamfield/blocks/result_numeric.html",
    )
    text = blocks.RichTextBlock(required=False, label="Textual results")
    image = ImageChooserBlock(required=False)
    remove_desaturation_filter = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Do not apply a desaturation filter to the image.",
    )
    logo = ImageChooserBlock(required=False)

    class Meta:
        icon = "bars"
        value_class = CaseStudyStructValue
        template = ("patterns/molecules/streamfield/blocks/featured_case_study.html",)
        group = "Custom"

    def clean(self, value):
        struct_value = super().clean(value)
        errors = {}

        numeric_results = value.get("numeric_results")
        text = value.get("text")

        if numeric_results and text:
            error_message = "Add either numeric results or text but not both."
            errors["numeric_results"] = ErrorList([ValidationError(error_message)])
            errors["text"] = ErrorList([ValidationError(error_message)])

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value


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
        group = "Custom"


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
        group = "Custom"


class EventLinkStructValue(ButtonLinkStructValue):
    def get_button_link_block(self):
        return self.get("url")[0]


class EventBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    url = blocks.StreamBlock(
        [
            ("internal_link", blocks.PageChooserBlock()),
            ("external_link", blocks.URLBlock()),
            ("email", blocks.EmailBlock()),
        ],
        required=True,
        max_num=1,
    )
    type = blocks.ListBlock(
        SnippetChooserBlock("torchbox.EventType"),
        min_num=1,
    )
    start_date = blocks.DateBlock()
    start_time = blocks.TimeBlock(required=False)
    end_date = blocks.DateBlock(required=False)
    end_time = blocks.TimeBlock(required=False)
    location = blocks.TextBlock(required=False)
    image = ImageChooserBlock()
    secondary_link = LinkBlock(required=False, label="Secondary link")

    class Meta:
        icon = "date"
        template = "patterns/molecules/streamfield/blocks/event_block.html"
        value_class = EventLinkStructValue
        group = "Calls to action"

    def clean(self, value):
        struct_value = super().clean(value)

        errors = {}
        start_date = value.get("start_date")
        start_time = value.get("start_time")
        end_date = value.get("end_date")
        end_time = value.get("end_time")

        if end_date and end_date < start_date:
            errors["end_date"] = ErrorList(
                [ValidationError("End date cannot be earlier than start date.")]
            )
        if start_time and end_date and not end_time:
            errors["end_time"] = ErrorList(
                [
                    ValidationError(
                        "End time is required if start time and end date are set."
                    )
                ]
            )
        if (
            end_date
            and end_date == start_date
            and end_time
            and start_time
            and end_time < start_time
        ):
            errors["end_time"] = ErrorList(
                [
                    ValidationError(
                        "End time cannot be earlier than start time on the same day."
                    )
                ]
            )
        if errors:
            raise StructBlockValidationError(errors)
        return struct_value


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
        group = "Calls to action"


class TabbedParagraphBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    intro = blocks.TextBlock(label="Introduction")
    tabbed_paragraph_sections = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("name", blocks.CharBlock()),
                ("summary", blocks.TextBlock()),
                ("text", blocks.RichTextBlock()),
                ("button_text", blocks.CharBlock(required=False)),
                ("button_link", blocks.PageChooserBlock(required=False)),
            ],
            help_text="Add a tabbed paragraph, with a name, summary, text and an optional page link & button text",
            icon="breadcrumb-expand",
        ),
        min_num=2,
        help_text="Add at least two tabbed paragraph sections",
    )

    def clean(self, value):
        value = super().clean(value)
        errors = defaultdict(ErrorList)
        non_block_errors = ErrorList()

        for tabbed_paragraph_section in value["tabbed_paragraph_sections"]:
            button_values = {
                "button_link": tabbed_paragraph_section["button_link"],
                "button_text": tabbed_paragraph_section["button_text"],
            }

            if any(button_values.values()) and not all(button_values.values()):
                message = "There must be a value for both button link and text, if one has a value."

                for key, value in button_values.items():
                    if not value:
                        errors[key].append(message)
                        non_block_errors.append(ValidationError(message))

        if errors:
            raise blocks.StructBlockValidationError(
                block_errors=errors, non_block_errors=non_block_errors
            )

        return value

    class Meta:
        icon = "list-ul"
        template = "patterns/molecules/streamfield/blocks/tabbed_paragraph_block.html"
        group = "Custom"


class PhotoCollageBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    intro = blocks.TextBlock(label="Introduction")
    button_link = blocks.StreamBlock(
        [
            ("internal_link", blocks.PageChooserBlock()),
            ("external_link", blocks.URLBlock()),
        ],
        required=False,
        max_num=1,
    )
    button_text = blocks.CharBlock(
        required=False,
        max_length=55,
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
        button_link = value.get("button_link")
        button_text = value.get("button_text")

        if button_link and not button_text:
            error = ErrorList(
                [ValidationError("You must add button text for the button link.")]
            )
            errors["button_text"] = error

        if button_text and not button_link:
            error = ErrorList(
                [
                    ValidationError(
                        "You must specify a button link above, for the button text you have provided."
                    )
                ]
            )
            errors["button_text"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value

    class Meta:
        icon = "image"
        template = "patterns/molecules/streamfield/blocks/photo_collage_block.html"
        value_class = ButtonLinkStructValue
        group = "Custom"


class EmbedBlock(WagtailEmbedBlock):
    def get_embed_instance(self, value):
        try:
            return get_embed(value.url)
        except EmbedException as e:
            logger.exception("Embed exception: %s", e)
            return None

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if embed := self.get_embed_instance(value):
            context["thumbnail_url"] = embed.thumbnail_url
            context["is_youtube"] = embed.provider_name.lower() == "youtube"
        return context

    class Meta:
        icon = "code"
        template = "patterns/molecules/streamfield/blocks/embed_block.html"


class StoryBlock(blocks.StreamBlock):
    h2 = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading2_block.html",
        group="Basics",
    )
    h3 = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading3_block.html",
        group="Basics",
    )
    h4 = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="patterns/molecules/streamfield/blocks/heading4_block.html",
        group="Basics",
    )
    intro = blocks.RichTextBlock(
        icon="pilcrow",
        template="patterns/molecules/streamfield/blocks/intro_block.html",
        group="Basics",
    )
    paragraph = blocks.RichTextBlock(
        icon="pilcrow",
        template="patterns/molecules/streamfield/blocks/paragraph_block.html",
        group="Basics",
    )
    image = ImageBlock(
        template="patterns/molecules/streamfield/blocks/image_block.html",
        group="Media and images",
    )
    wide_image = ImageBlock(
        template="patterns/molecules/streamfield/blocks/wide_image_block.html",
        group="Media and images",
    )
    call_to_action = CallToActionBlock(
        label="Call to Action",
        template="patterns/molecules/streamfield/blocks/call_to_action.html",
        group="Calls to action",
    )
    contact_call_to_action = ContactCTABlock(
        label="Contact Call to Action",
        template="patterns/molecules/streamfield/blocks/contact_call_to_action.html",
        group="Calls to action",
    )
    pullquote = PullQuoteBlock(
        template="patterns/molecules/streamfield/blocks/pullquote_block.html",
        group="Basics",
    )
    raw_html = blocks.RawHTMLBlock(
        label="Raw HTML",
        icon="code",
        template="patterns/molecules/streamfield/blocks/raw_html_block.html",
        group="Special",
    )
    mailchimp_form = blocks.RawHTMLBlock(
        label="Mailchimp embedded form",
        icon="code",
        template="patterns/molecules/streamfield/blocks/mailchimp_form_block.html",
        group="Special",
    )
    markdown = MarkdownBlock(
        label="Code block",
        icon="code",
        template="patterns/molecules/streamfield/blocks/markdown_block.html",
        group="Special",
        help_text="""
            Use this block to add code snippets.
            Don't use it for headings or other markdown content,
            as they will not be styled correctly.
            To use syntax highlighting, specify the language after the triple backticks, e.g.:
            ```python
            """,
    )
    embed = EmbedBlock(
        group="Media and images",
    )
    video_block = VideoBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"


class HomePageStoryBlock(blocks.StreamBlock):
    showcase = ShowcaseBlock()
    featured_case_study = FeaturedCaseStudyBlock()
    blog_chooser = BlogChooserBlock()
    work_chooser = WorkChooserBlock()
    photo_collage = PhotoCollageBlock()
    promo = PromoBlock()
    tabbed_paragraph = TabbedParagraphBlock()
    event = EventBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
