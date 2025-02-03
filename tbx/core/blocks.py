from collections import defaultdict
from datetime import datetime
import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.utils import ErrorList
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.contrib.typed_table_block.blocks import (
    TypedTableBlock as WagtailTypedTableBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock as WagtailEmbedBlock
from wagtail.embeds.embeds import get_embed
from wagtail.embeds.exceptions import EmbedException
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock

from wagtailmarkdown.blocks import MarkdownBlock
from wagtailmedia.blocks import VideoChooserBlock

from tbx.images.models import CustomImage


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


class CustomImageChooserBlock(ImageChooserBlock):
    """A custom ImageChooserBlock that prefetches the image renditions"""

    def to_python(self, value):
        if value is None:
            return value
        else:
            try:
                return self.model_class.objects.prefetch_renditions().get(pk=value)
            except self.model_class.DoesNotExist:
                return None

    def bulk_to_python(self, values):
        objects = self.model_class.objects.prefetch_renditions().in_bulk(values)
        return [
            objects.get(_id) for _id in values
        ]  # Keeps the ordering the same as in values.


class ImageFormatChoiceBlock(blocks.FieldBlock):
    """
    This block is no longer in use. However, because several migrations
    make explicit references to the block class, we cannot remove it
    without breaking the migrations.
    See https://github.com/wagtail/wagtail/issues/3710 for more details.
    """


class AltTextStructValue(blocks.StructValue):
    def image_alt_text(self):
        if custom_alt_text := self.get("alt_text"):
            return custom_alt_text
        return self.get("image").title


class ImageWithAltTextBlock(blocks.StructBlock):
    """
    Allows for specifying optional alt text for an image.
    """

    image = CustomImageChooserBlock()
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
    image = CustomImageChooserBlock()
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
        elif block_type == "document_link":
            return block.value.file.url

        return ""

    def get_button_file_size(self):
        block = self.get_button_link_block()
        if block.block_type == "document_link":
            return block.value.file.size


class CallToActionBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, max_length=255)
    description = blocks.RichTextBlock(
        features=settings.PARAGRAPH_RICH_TEXT_FEATURES, required=False
    )
    button_text = blocks.CharBlock(max_length=55)
    button_link = blocks.StreamBlock(
        [
            ("internal_link", blocks.PageChooserBlock()),
            ("external_link", blocks.URLBlock()),
            ("email", blocks.EmailBlock()),
            ("document_link", DocumentChooserBlock()),
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


class DynamicHeroBlock(blocks.StructBlock):
    """
    This block displays text that will be cycled through.
    """

    static_text = blocks.CharBlock(required=False)
    dynamic_text = blocks.ListBlock(
        blocks.CharBlock(),
        help_text=(
            "The hero will cycle through these texts on larger screen sizes "
            "and only show the first text on smaller screen sizes."
        ),
        required=False,
    )

    class Meta:
        icon = "title"
        template = "patterns/molecules/streamfield/blocks/dynamic_hero_block.html"


class FeaturedPageCardBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(features=settings.NO_HEADING_RICH_TEXT_FEATURES)
    image = ImageChooserBlock()
    link_text = blocks.CharBlock()
    accessible_link_text = blocks.CharBlock(
        help_text=(
            "Used by screen readers. This should be descriptive for accessibility. "
            'If not filled, the "Link text" field will be used instead.'
        ),
        required=False,
    )
    page = blocks.PageChooserBlock()

    class Meta:
        icon = "breadcrumb-expand"


class FeaturedServicesBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=False)
    intro = blocks.RichTextBlock(
        features=settings.NO_HEADING_RICH_TEXT_FEATURES, required=False
    )
    cards = blocks.ListBlock(
        FeaturedPageCardBlock(),
        max_num=4,
        min_num=2,
    )

    class Meta:
        group = "Custom"
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/featured_services_block.html"


class FourPhotoCollageBlock(blocks.StructBlock):
    """
    Accepts 4 photos shown as a collage + text below.
    Used on the division page and the service area page.
    """

    images = blocks.ListBlock(
        ImageWithAltTextBlock(label="Photo"),
        min_num=4,
        max_num=4,
        label="Photos",
        help_text="Exactly four required.",
        default=[{"image": None, "alt_text": ""}] * 4,
    )
    caption = blocks.RichTextBlock(
        features=settings.PARAGRAPH_RICH_TEXT_FEATURES, required=False
    )
    description = blocks.RichTextBlock(
        features=settings.PARAGRAPH_RICH_TEXT_FEATURES, required=False
    )

    class Meta:
        group = "Custom"
        icon = "image"
        template = "patterns/molecules/streamfield/blocks/four_photo_collage_block.html"


class KeyPointIconChoice(models.TextChoices):
    CALENDAR = "key-calendar", "calendar icon"
    CONVERSATION = "key-conversation", "chat bubbles icon"
    LIGHTBULB = "key-lightbulb", "lightbulb icon"
    MAIL = "key-mail", "mail icon"
    MEGAPHONE = "key-megaphone", "megaphone icon"
    PEOPLE = "key-people", "people icon"
    BULLSEYE = "key-bullseye", "target icon"
    UP_ARROW = "key-up-arrow", "up arrow icon"


class IconKeyPointBlock(blocks.StructBlock):
    icon = blocks.ChoiceBlock(
        choices=KeyPointIconChoice.choices,
        default=KeyPointIconChoice.LIGHTBULB,
        max_length=32,
    )
    icon_label = blocks.CharBlock()
    heading = blocks.CharBlock()
    description = blocks.RichTextBlock(features=settings.NO_HEADING_RICH_TEXT_FEATURES)

    class Meta:
        icon = "breadcrumb-expand"


class IconKeyPointsBlock(blocks.StructBlock):
    """Used on the service area page."""

    title = blocks.CharBlock(max_length=255, required=False)
    intro = blocks.RichTextBlock(
        features=settings.NO_HEADING_RICH_TEXT_FEATURES, required=False
    )
    key_points = blocks.ListBlock(IconKeyPointBlock(label="Key point"), min_num=1)

    class Meta:
        group = "Custom"
        icon = "list-ul"
        template = "patterns/molecules/streamfield/blocks/icon_keypoints_block.html"


class IntroductionWithImagesBlock(blocks.StructBlock):
    """Used on the division page."""

    introduction = blocks.RichTextBlock(features=settings.PARAGRAPH_RICH_TEXT_FEATURES)
    description = blocks.RichTextBlock(
        blank=True, features=settings.NO_HEADING_RICH_TEXT_FEATURES
    )
    images = blocks.ListBlock(
        ImageWithAltTextBlock(label="Photo"),
        min_num=2,
        max_num=2,
        label="Photos",
        help_text="Exactly two required.",
        default=[{"image": None, "alt_text": ""}] * 2,
    )

    class Meta:
        group = "Custom"
        icon = "pilcrow"
        template = (
            "patterns/molecules/streamfield/blocks/introduction_with_images_block.html"
        )


class LinkColumnsBlock(blocks.StructBlock):
    """
    Displays a list of links in columns.
    Used on the service area page.
    """

    title = blocks.CharBlock(max_length=255, required=False)
    intro = blocks.RichTextBlock(
        features=settings.NO_HEADING_RICH_TEXT_FEATURES, required=False
    )
    links = LinkBlock(max_num=None, min_num=1)

    class Meta:
        group = "Custom"
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/link_columns_block.html"


class PartnersBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=False)
    partner_logos = blocks.ListBlock(CustomImageChooserBlock(), label="Logos")

    class Meta:
        icon = "openquote"
        label = "Partner logos"
        template = "patterns/molecules/streamfield/blocks/partners_block.html"
        group = "Custom"


class ShowcaseBlock(blocks.StructBlock):
    """
    This block is a standard ShowcaseBlock, available on the home page and
    service page templates. See also the HomepageShowcaseBlock.
    """

    title = blocks.CharBlock(max_length=255, required=False)
    showcase_paragraphs = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("heading", blocks.CharBlock()),
                ("summary", blocks.RichTextBlock()),
                ("page", blocks.PageChooserBlock(required=False)),
            ],
            help_text="Add a showcase paragraph, with heading, summary text and an optional page link",
            icon="breadcrumb-expand",
        ),
        min_num=2,
        max_num=10,
        help_text="Add at least two showcase paragraphs",
    )

    class Meta:
        icon = "tasks"
        # Same template as the homepage showcase block
        template = "patterns/molecules/streamfield/blocks/showcase_block.html"
        group = "Custom"


class IconChoice(models.TextChoices):
    LIGHTBULB = "lightbulb", "lightbulb icon"
    TARGET = "target", "target icon"
    MEGAPHONE = "megaphone", "megaphone icon"
    WAGTAIL = "wagtail", "wagtail icon"


class DivisionSignpostCardBlock(blocks.StructBlock):
    class ColourTheme(models.TextChoices):
        CORAL = "theme-coral", "Coral"
        NEBULINE = "theme-nebuline", "Nebuline"
        LAGOON = "theme-lagoon", "Lagoon"

    card_colour = blocks.ChoiceBlock(
        choices=ColourTheme.choices, default=ColourTheme.CORAL, max_length=20
    )
    heading = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(features=settings.NO_HEADING_RICH_TEXT_FEATURES)
    image = ImageChooserBlock()
    link_text = blocks.CharBlock()
    accessible_link_text = blocks.CharBlock(
        help_text=(
            "Used by screen readers. This should be descriptive for accessibility. "
            'If not filled, the "Link text" field will be used instead.'
        ),
        required=False,
    )
    page = blocks.PageChooserBlock()

    class Meta:
        icon = "breadcrumb-expand"


class DivisionSignpostBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=False)
    intro = blocks.RichTextBlock(
        features=settings.NO_HEADING_RICH_TEXT_FEATURES, required=False
    )
    cards = blocks.ListBlock(
        DivisionSignpostCardBlock(),
        max_num=3,
        min_num=3,
    )

    class Meta:
        group = "Custom"
        icon = "thumbtack"
        template = "patterns/molecules/streamfield/blocks/division_signpost_block.html"


class HomepageShowcaseBlock(blocks.StructBlock):
    """
    This block is similar to the ShowcaseBlock, but is rendered larger
    and with icons. It is only available on the home page template.
    Unlike the standard showcase block, this includes and intro,
    and page links are required. It shares a template and styling with the standard
    showcase, but with some variations.
    """

    title = blocks.CharBlock(max_length=255)
    intro = blocks.TextBlock(required=False)
    showcase_paragraphs = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("heading", blocks.CharBlock()),
                ("summary", blocks.RichTextBlock()),
                ("page", blocks.PageChooserBlock()),
                (
                    "icon",
                    blocks.ChoiceBlock(
                        max_length=9,
                        choices=IconChoice.choices,
                        default=IconChoice.LIGHTBULB,
                    ),
                ),
            ],
            help_text="Add a showcase paragraph, with icon, heading, summary text and a page link",
            icon="breadcrumb-expand",
        ),
        min_num=2,
        max_num=6,
        help_text="Add at least two showcase paragraphs",
    )

    class Meta:
        icon = "tasks"
        # Same template as the showcase block
        template = "patterns/molecules/streamfield/blocks/showcase_block.html"
        group = "Custom"

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        # Allows us to add some logic in the template to generate different markup
        # for the homepage showcase block and the showcase block
        ctx["is_homepage_showcase"] = True
        return ctx


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
        elif (
            page := self.get("link")
        ) and page.content_type.model_class().__name__ == "WorkPage":
            return page.specific.logo
        return None


class NumericResultBlock(blocks.StructBlock):
    label = blocks.CharBlock(
        max_length=255,
        help_text=mark_safe(  # noqa: S308
            "Short text to describe the change e.g. <strong>Raised over</strong>"
        ),
    )
    headline_number = blocks.CharBlock(
        max_length=255,
        help_text=mark_safe("A numerical value e.g. <strong>£600k</strong>"),  # noqa: S308
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
    intro = blocks.RichTextBlock(
        features=settings.NO_HEADING_RICH_TEXT_FEATURES, required=False
    )
    blog_pages = blocks.ListBlock(
        blocks.PageChooserBlock(page_type="blog.BlogPage"),
        min_num=1,
        max_num=3,
    )
    primary_button = LinkBlock(label="Primary button", required=False)
    secondary_button = LinkBlock(label="Secondary button", required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["is_standard_page"] = False
        return context

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/blog_chooser_block.html"
        group = "Custom"


class BlogChooserStandardPageBlock(BlogChooserBlock):
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["is_standard_page"] = True
        return context


class WorkChooserBlock(blocks.StructBlock):
    featured_work_heading = blocks.CharBlock(max_length=255)
    intro = blocks.RichTextBlock(
        features=settings.NO_HEADING_RICH_TEXT_FEATURES, required=False
    )
    work_pages = blocks.ListBlock(
        blocks.PageChooserBlock(page_type=["work.WorkPage", "work.HistoricalWorkPage"]),
        min_num=1,
        max_num=3,
    )
    primary_button = LinkBlock(label="Primary button", required=False)
    secondary_button = LinkBlock(label="Secondary button", required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        prefetch_listing_images = models.Prefetch(
            "header_image",
            queryset=CustomImage.objects.prefetch_renditions(
                "fill-370x370|format-webp",
                "fill-370x335|format-webp",
                "fill-740x740|format-webp",
                "fill-740x670|format-webp",
            ),
        )

        work_page_ids = [page.pk for page in value["work_pages"]]
        work_pages = (
            Page.objects.filter(pk__in=work_page_ids)
            .live()
            .public()
            .defer_streamfields()
            .prefetch_related(prefetch_listing_images)
            .specific()
            .in_bulk()
        )
        # Keeps the ordering the same as in values.
        context["work_pages"] = [
            work_pages[_id] for _id in work_page_ids if _id in work_pages
        ]
        context["is_standard_page"] = False
        return context

    class Meta:
        icon = "link"
        template = "patterns/molecules/streamfield/blocks/work_chooser_block.html"
        group = "Custom"


class WorkChooserStandardPageBlock(WorkChooserBlock):
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["is_standard_page"] = True
        return context


class EventLinkStructValue(ButtonLinkStructValue):
    def get_button_link_block(self):
        return self.get("url")[0]

    def get_start_date_time(self) -> datetime:
        start_date = self.get("start_date")
        start_time = self.get("start_time")
        if start_time:
            return timezone.make_aware(datetime.combine(start_date, start_time))
        return timezone.make_aware(datetime.combine(start_date, datetime.min.time()))

    def get_end_date_time(self) -> datetime | None:
        end_date = self.get("end_date")
        end_time = self.get("end_time")
        if end_date and end_time:
            return timezone.make_aware(datetime.combine(end_date, end_time))
        return None


class BaseEventBlock(blocks.StructBlock):
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
    location = blocks.TextBlock(required=False)
    start_date = blocks.DateBlock()
    start_time = blocks.TimeBlock(required=False)
    end_date = blocks.DateBlock(required=False)
    end_time = blocks.TimeBlock(required=False)

    class Meta:
        icon = "date"
        value_class = EventLinkStructValue

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


class EventBlock(BaseEventBlock):
    image = CustomImageChooserBlock()
    secondary_link = LinkBlock(required=False, label="Secondary link")

    class Meta:
        template = "patterns/molecules/streamfield/blocks/event_block.html"
        group = "Calls to action"


class PromoBlock(blocks.StructBlock):
    title = blocks.TextBlock()
    description = blocks.TextBlock()
    image = CustomImageChooserBlock()
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


class TabbedParagraphSectionsListBlock(blocks.ListBlock):
    def clean(self, value):
        result = super().clean(value)
        errors = {}

        for i in range(len(result)):
            button_values = {
                "button_link": result[i]["button_link"],
                "button_text": result[i]["button_text"],
                "button_url": result[i]["button_url"],
            }

            item_errors = ErrorList()

            if button_values.get("button_link") and button_values.get("button_url"):
                item_errors.append(
                    ValidationError(
                        "You must specify either a page link or a URL, not both."
                    )
                )

            if button_values.get("button_text") and (
                not button_values.get("button_link")
                and not button_values.get("button_url")
            ):
                item_errors.append(
                    "You must specify a button link or URL for the button text you have provided."
                )

            if item_errors:
                errors[i] = item_errors

        if errors:
            raise blocks.ListBlockValidationError(block_errors=errors)

        return result


class TabbedParagraphBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=False)
    intro = blocks.RichTextBlock(label="Introduction", required=False)
    tabbed_paragraph_sections = TabbedParagraphSectionsListBlock(
        blocks.StructBlock(
            [
                ("name", blocks.CharBlock()),
                ("summary", blocks.TextBlock()),
                ("text", blocks.RichTextBlock()),
                ("button_text", blocks.CharBlock(required=False)),
                ("button_link", blocks.PageChooserBlock(required=False)),
                ("button_url", blocks.URLBlock(required=False)),
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

        if value["intro"] and not value["title"]:
            message = "You cannot add an intro without also adding a title"
            errors["title"].append(ValidationError(message))

        if errors:
            raise blocks.StructBlockValidationError(block_errors=errors)

        return value

    class Meta:
        icon = "list-ul"
        template = "patterns/molecules/streamfield/blocks/tabbed_paragraph_block.html"
        group = "Custom"


class PhotoCollageBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=False)
    intro = blocks.TextBlock(label="Introduction", required=False)
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

        has_button = bool(button_link and button_text)
        has_intro = bool(value.get("intro"))

        if (has_intro or has_button) and not value["title"]:
            error = ErrorList(
                [
                    ValidationError(
                        "You cannot add a button or intro without also adding a title"
                    )
                ]
            )
            errors["title"] = error

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
            raise blocks.StructBlockValidationError(block_errors=errors)
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


class NumericStatisticsBlock(blocks.StructBlock):
    headline_number = blocks.CharBlock(
        max_length=255,
        help_text=mark_safe("A numerical value e.g. <strong>30%</strong>"),  # noqa: S308
    )
    description = blocks.TextBlock(
        help_text=mark_safe(  # noqa: S308
            "Text to describe the change e.g. <strong>Reduction in accessibility errors</strong>"
        )
    )
    further_details = blocks.TextBlock(
        required=False,
        help_text=mark_safe(  # noqa: S308
            "Text to give more information, e.g. <strong>Over 80% of pages</strong>"
        ),
    )

    class Meta:
        icon = "table"
        label_format = "{headline_number} {description} {further_details}"


class NumericStatisticsGroupBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, required=False)
    intro = blocks.RichTextBlock(
        features=settings.NO_HEADING_RICH_TEXT_FEATURES, required=False
    )
    statistics = blocks.ListBlock(
        NumericStatisticsBlock(),
        max_num=4,
        min_num=1,
    )

    class Meta:
        group = "Custom"
        icon = "table"
        label = "Numeric statistics"
        template = (
            "patterns/molecules/streamfield/blocks/numeric_stats_group_block.html"
        )


class TextualStatisticsBlock(blocks.StructBlock):
    headline_text = blocks.CharBlock(
        max_length=255,
        help_text=mark_safe(  # noqa: S308
            "Describe a general improvement, e.g. <strong>Reduction in accessibility issues</strong>"
        ),
    )
    further_details = blocks.TextBlock(
        required=False,
        help_text=mark_safe(  # noqa: S308
            "Text to give more information, e.g. <strong>Over 80% of pages</strong>"
        ),
    )

    class Meta:
        icon = "info-circle"


class TypedTableBlock(blocks.StructBlock):
    table = WagtailTypedTableBlock(
        [
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=["bold", "italic", "link", "ol", "ul", "document-link"]
                ),
            ),
        ]
    )

    class Meta:
        icon = "table"
        template = "patterns/molecules/streamfield/blocks/typed_table_block.html"


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
    typed_table = TypedTableBlock(label="Table block", group="Basics")
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


class StandardPageStoryBlock(StoryBlock):
    promo = PromoBlock()
    blog_chooser = BlogChooserStandardPageBlock()
    work_chooser = WorkChooserStandardPageBlock()


class HomePageStoryBlock(blocks.StreamBlock):
    division_signpost = DivisionSignpostBlock()
    showcase = ShowcaseBlock(label="Standard showcase")
    homepage_showcase = HomepageShowcaseBlock(label="Large showcase with icons")
    featured_case_study = FeaturedCaseStudyBlock()
    blog_chooser = BlogChooserBlock()
    work_chooser = WorkChooserBlock()
    photo_collage = PhotoCollageBlock()
    promo = PromoBlock()
    tabbed_paragraph = TabbedParagraphBlock()
    event = EventBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
