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

    def test_label_required_when_no_link(self):
        from wagtail.blocks.struct_block import StructBlockValidationError

        value = self._value(
            title="",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.MIXED_LIST,
        )
        with self.assertRaises(StructBlockValidationError):
            self.block.clean(value)
