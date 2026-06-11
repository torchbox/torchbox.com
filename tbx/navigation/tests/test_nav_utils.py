from django.test import TestCase

import wagtail_factories

from tbx.core.factories import HomePageFactory
from tbx.navigation.blocks import PrimaryNavLinkBlock
from tbx.navigation.utils import (
    format_nav_tags,
    item_has_dropdown,
    resolve_primary_nav_dropdown,
)
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.work.factories import WorkIndexPageFactory


class TestResolvePrimaryNavDropdown(TestCase):
    def setUp(self):
        root_page = wagtail_factories.PageFactory(parent=None)
        self.home_page = HomePageFactory(parent=root_page)
        self.work_index = WorkIndexPageFactory(parent=self.home_page)
        self.block = PrimaryNavLinkBlock()

    def test_manual_mixed_list_dropdown(self):
        value = self.block.to_python(
            {
                "page": self.home_page.pk,
                "external_link": "",
                "title": "Services",
                "dropdown_style": "mixed_list",
                "content_source": "manual",
                "secondary_heading": "Core services",
                "promoted_heading": "Quick start",
                "secondary_links": [
                    {
                        "type": "link",
                        "value": {
                            "page": self.home_page.pk,
                            "external_link": "",
                            "title": "Websites",
                            "description": "Platforms and websites",
                            "tags": "",
                            "accent_colour": "",
                        },
                    }
                ],
                "promoted_links": [
                    {
                        "type": "link",
                        "value": {
                            "page": self.home_page.pk,
                            "external_link": "",
                            "title": "Website audit",
                            "description": "A full review",
                        },
                    }
                ],
                "page_children_depth": "2",
            }
        )

        dropdown = resolve_primary_nav_dropdown(value)
        self.assertEqual(dropdown["style"], "mixed_list")
        self.assertEqual(dropdown["secondary_heading"], "Core services")
        self.assertEqual(len(dropdown["secondary_items"]), 1)
        self.assertEqual(dropdown["secondary_items"][0].text, "Websites")
        self.assertEqual(len(dropdown["promoted_items"]), 1)
        self.assertTrue(item_has_dropdown(value))

    def test_auto_taxonomy_dropdown(self):
        SectorFactory(name="Charities", slug="charities", sort_order=1)
        ServiceFactory(name="SEO", slug="seo", sort_order=1)

        value = self.block.to_python(
            {
                "page": self.work_index.pk,
                "external_link": "",
                "title": "Work",
                "dropdown_style": "taxonomy_index",
                "content_source": "auto_taxonomy",
                "secondary_heading": "",
                "promoted_heading": "",
                "secondary_links": [],
                "promoted_links": [],
                "page_children_depth": "2",
            }
        )

        dropdown = resolve_primary_nav_dropdown(value)
        self.assertEqual(dropdown["style"], "taxonomy_index")
        self.assertEqual(dropdown["secondary_heading"], "By sector")
        self.assertEqual(dropdown["promoted_heading"], "By service")
        self.assertEqual(len(dropdown["secondary_items"]), 1)
        self.assertIn("filter=charities", dropdown["secondary_items"][0].url)
        self.assertIn("filter=seo", dropdown["promoted_items"][0].url)

    def test_page_children_dropdown(self):
        child = HomePageFactory(parent=self.home_page, title="Child page")
        child.show_in_menus = True
        child.save()

        value = self.block.to_python(
            {
                "page": self.home_page.pk,
                "external_link": "",
                "title": "About",
                "dropdown_style": "mixed_list",
                "content_source": "page_children",
                "secondary_heading": "",
                "promoted_heading": "",
                "secondary_links": [],
                "promoted_links": [],
                "page_children_depth": "1",
            }
        )

        dropdown = resolve_primary_nav_dropdown(value)
        self.assertIsNotNone(dropdown)
        self.assertEqual(dropdown["style"], "mixed_list")
        self.assertEqual(len(dropdown["secondary_items"]), 1)
        self.assertEqual(dropdown["secondary_items"][0].text, "Child page")

    def test_no_dropdown_when_style_none(self):
        value = self.block.to_python(
            {
                "page": self.home_page.pk,
                "external_link": "",
                "title": "Home",
                "dropdown_style": "none",
                "content_source": "manual",
                "secondary_heading": "",
                "promoted_heading": "",
                "secondary_links": [],
                "promoted_links": [],
                "page_children_depth": "2",
            }
        )

        self.assertFalse(item_has_dropdown(value))
        self.assertIsNone(resolve_primary_nav_dropdown(value))

    def test_format_nav_tags(self):
        self.assertEqual(format_nav_tags("SEO, PPC"), "SEO · PPC")
        self.assertEqual(format_nav_tags("SEO · PPC"), "SEO · PPC")
        self.assertEqual(format_nav_tags(""), "")
