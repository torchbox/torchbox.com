from django.test import TestCase

from ..utils.formatting import (
    convert_bold_links_to_pink,
    convert_italic_links_to_purple,
)


class ConvertBoldLinksToPinkTestCase(TestCase):
    def test_doesnt_convert_non_link(self):
        html_text = "<b>Hello</b> world <b><i>foo</i></b> bar"
        result = convert_bold_links_to_pink(html_text)
        self.assertEqual(html_text, result)

    def test_convert_link(self):
        html_text = '<a href="#"><b>Hello</b> world <b><i>foo</i></b> bar</a>'
        result = convert_bold_links_to_pink(html_text)
        self.assertEqual(
            result,
            (
                '<a href="#"><span class="text-coral">Hello</span> world '
                '<span class="text-coral"><i>foo</i></span> bar</a>'
            ),
        )


class ConvertItalicLinksToPurpleTestCase(TestCase):
    def test_doesnt_convert_non_link(self):
        html_text = "<i>Hello</i> world <b><i>foo</i></b> bar"
        result = convert_italic_links_to_purple(html_text)
        self.assertEqual(html_text, result)

    def test_convert_link(self):
        html_text = '<a href="#"><i>Hello</i> world <b><i>foo</i></b> bar</a>'
        result = convert_italic_links_to_purple(html_text)
        self.assertEqual(
            result,
            (
                '<a href="#"><span class="text-nebuline">Hello</span> world '
                '<b><span class="text-nebuline">foo</span></b> bar</a>'
            ),
        )
