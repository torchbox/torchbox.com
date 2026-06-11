from django.core.exceptions import ValidationError
from django.db import models
from django.forms.utils import ErrorList

from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError

from tbx.core.blocks import CustomImageChooserBlock


class LinkBlockStructValue(blocks.StructValue):
    def url(self):
        if page := self.get("page"):
            return page.url

        if external_link := self.get("external_link"):
            return external_link

        return ""

    def text(self):
        if self.get("page") and not self.get("title"):
            return self.get("page").title
        if title := self.get("title"):
            return title
        return ""

    def is_page(self):
        return bool(self.get("page"))


class LinkValidationMixin:
    """
    Ensures that you cannot select both an external and an internal link.
    Used by both LinkBlock FooterLinkBlock
    """

    def clean(self, value):
        struct_value = super().clean(value)

        errors = {}
        page = value.get("page")
        external_link = value.get("external_link")

        if not page and not external_link:
            error = ErrorList(
                [ValidationError("You must specify either a page or an external link")]
            )
            errors["page"] = errors["external_link"] = error

        if page and external_link:
            error = ErrorList(
                [
                    ValidationError(
                        "You must specify either a page or an external link, not both"
                    )
                ]
            )
            errors["external_link"] = errors["page"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value


class LinkBlock(LinkValidationMixin, blocks.StructBlock):
    """
    Used to select links for the primary navigation and for the footer links
    """

    page = blocks.PageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title",
        required=False,
        label="Navigation text",
    )

    class Meta:
        value_class = LinkBlockStructValue

    def clean(self, value):
        """
        Additional validation to ensure that a link title is specified for external links
        """
        struct_value = super().clean(value)

        errors = {}
        external_link = value.get("external_link")

        if not value.get("title") and external_link:
            error = ErrorList(
                [ValidationError("You must specify the link title for external links")]
            )
            errors["title"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value


class SecondaryNavLinkBlock(LinkBlock):
    """Dropdown promoted/featured link with optional description."""

    description = blocks.TextBlock(required=False)


class FooterLinkBlock(LinkValidationMixin, blocks.StructBlock):
    """
    Used to select links for the footer logos
    """

    page = blocks.PageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False)

    class Meta:
        value_class = LinkBlockStructValue


ACCENT_COLOUR_CHOICES = [
    ("theme-coral", "Coral"),
    ("theme-nebuline", "Nebuline"),
    ("theme-lagoon", "Lagoon"),
    ("theme-green", "Green"),
    ("theme-earth", "Earth"),
]


class NavTeaserLinkBlock(SecondaryNavLinkBlock):
    tags = blocks.CharBlock(
        required=False,
        help_text="Optional sub-items, separated by middle dots when displayed",
    )
    accent_colour = blocks.ChoiceBlock(
        choices=ACCENT_COLOUR_CHOICES,
        required=False,
        label="Accent colour",
    )


class PrimaryNavLinkBlock(LinkBlock):
    class DropdownStyle(models.TextChoices):
        NONE = "none", "No dropdown"
        TEASER_GRID = "teaser_grid", "Teaser grid / card list"
        MIXED_LIST = "mixed_list", "Mixed list + featured links"
        TAXONOMY_INDEX = "taxonomy_index", "Taxonomy index"

    class ContentSource(models.TextChoices):
        MANUAL = "manual", "Manual links"
        AUTO_DIVISIONS = "auto_divisions", "Auto-generate from division pages"
        AUTO_TAXONOMY = "auto_taxonomy", "Auto-generate sectors and services"
        PAGE_CHILDREN = "page_children", "Auto-generate from page children"

    class PageChildrenDepth(models.TextChoices):
        LEVEL1 = "1", "Children only"
        LEVEL2 = "2", "Children and grandchildren"

    dropdown_style = blocks.ChoiceBlock(
        choices=DropdownStyle.choices,
        default=DropdownStyle.NONE,
        icon="list-ul",
        help_text="Choose how this item's dropdown is displayed.",
    )
    content_source = blocks.ChoiceBlock(
        choices=ContentSource.choices,
        default=ContentSource.MANUAL,
        icon="cogs",
        help_text="Choose whether dropdown links are edited manually or generated "
        "from site content. Manual link fields below are only used when this is set "
        "to “Manual links”.",
    )
    secondary_heading = blocks.CharBlock(
        required=False,
        help_text="Heading for the main column of dropdown links.",
    )
    promoted_heading = blocks.CharBlock(
        required=False,
        help_text="Heading for featured or promoted dropdown links.",
    )
    secondary_links = blocks.StreamBlock(
        [("link", NavTeaserLinkBlock(icon="link"))],
        required=False,
        help_text="Main dropdown links. Only used when content source is “Manual links”.",
    )
    promoted_links = blocks.StreamBlock(
        [("link", SecondaryNavLinkBlock(icon="link"))],
        required=False,
        help_text="Featured dropdown links. Only used when content source is “Manual links”.",
    )
    page_children_depth = blocks.ChoiceBlock(
        choices=PageChildrenDepth.choices,
        default=PageChildrenDepth.LEVEL2,
        required=False,
        icon="collapse-down",
        help_text="Only used when content source is “Auto-generate from page children”. "
        "Includes child pages with “Show in menus” enabled.",
    )


class FooterLogoBlock(blocks.StructBlock):
    image = CustomImageChooserBlock()
    link = FooterLinkBlock()
    alt_text = blocks.CharBlock(
        label="Alt text",
        help_text="The image title will be used if this is left blank.",
        required=False,
    )
