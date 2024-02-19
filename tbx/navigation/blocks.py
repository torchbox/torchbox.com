from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.blocks import ImageChooserBlock


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
        return self.get("title")

    def is_page(self):
        return bool(self.get("page"))


class LinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title", required=False
    )

    class Meta:
        value_class = LinkBlockStructValue

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

        if not value.get("title") and external_link:
            error = ErrorList(
                [ValidationError("You must specify the link title for external links")]
            )
            errors["title"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value


class PrimaryNavLinkBlock(LinkBlock):
    hide_children = blocks.BooleanBlock(
        required=False,
        label="Do not show child pages",
        help_text=mark_safe(
            "By default, the navigation menu displays the children and grandchildren of the "
            "selected page if their <strong>Show in menus</strong> checkbox is checked.<br />"
            "If you tick this checkbox, the navigation will exclude them, regardless of "
            "their <strong>Show in menus</strong> settings."
        ),
    )


class FooterLogoBlock(blocks.StructBlock):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Modify the help_text for the title field in the LinkBlock
        self.child_blocks["link"].child_blocks[
            "title"
        ].field.help_text = "This is used as the basis for alt text."

    image = ImageChooserBlock()
    link = LinkBlock()
