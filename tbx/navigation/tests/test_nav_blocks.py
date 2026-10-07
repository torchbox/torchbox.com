from django.test import TestCase

from tbx.navigation.blocks import PrimaryNavLinkBlock


class PrimaryNavLinkBlockCleanTests(TestCase):
    def setUp(self):
        self.block = PrimaryNavLinkBlock()

    def _value(self, **overrides):
        base = {
            "page": None,
            "external_link": "",
            "title": "",
            "dropdown_style": PrimaryNavLinkBlock.DropdownStyle.NONE,
            "content_source": PrimaryNavLinkBlock.ContentSource.MANUAL,
            "main_heading": "",
            "supporting_heading": "",
            "main_links": [],
            "supporting_links": [],
            "page_children_depth": PrimaryNavLinkBlock.PageChildrenDepth.LEVEL2,
        }
        base.update(overrides)
        return self.block.to_python(base)

    def test_label_only_valid_when_dropdown_set(self):
        value = self._value(
            title="What we do",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.MIXED_LIST,
        )
        cleaned = self.block.clean(value)
        self.assertEqual(cleaned["title"], "What we do")

    def test_label_only_invalid_without_dropdown(self):
        from wagtail.blocks.struct_block import StructBlockValidationError

        value = self._value(
            title="What we do",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.NONE,
        )
        with self.assertRaises(StructBlockValidationError):
            self.block.clean(value)

    def test_no_dropdown_with_page_and_no_title_is_valid(self):
        """
        When dropdown_style == NONE and a page is set, title may be empty —
        the page title will be derived at render time via LinkBlockStructValue.text().
        """
        import wagtail_factories

        from tbx.core.factories import HomePageFactory

        root_page = wagtail_factories.PageFactory(parent=None)
        home_page = HomePageFactory(parent=root_page)

        value = self._value(
            page=home_page.pk,
            title="",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.NONE,
        )
        cleaned = self.block.clean(value)
        self.assertIsNotNone(cleaned["page"])

    def test_no_dropdown_with_external_link_and_no_title_is_invalid(self):
        """
        When dropdown_style == NONE and external_link is set (no page),
        title is required — there's no page title to fall back to.
        """
        from wagtail.blocks.struct_block import StructBlockValidationError

        value = self._value(
            page=None,
            external_link="https://example.com",
            title="",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.NONE,
        )
        with self.assertRaises(StructBlockValidationError) as ctx:
            self.block.clean(value)
        self.assertIn("title", ctx.exception.block_errors)

    def test_label_required_when_no_link(self):
        from wagtail.blocks.struct_block import StructBlockValidationError

        value = self._value(
            title="",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.MIXED_LIST,
        )
        with self.assertRaises(StructBlockValidationError):
            self.block.clean(value)
