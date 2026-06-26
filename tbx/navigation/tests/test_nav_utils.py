from types import SimpleNamespace

from django.test import TestCase

from wagtail.models import Site

import wagtail_factories

from tbx.core.factories import HomePageFactory
from tbx.navigation.blocks import PrimaryNavLinkBlock
from tbx.navigation.utils import (
    NAV_STYLE_NONE,
    format_nav_tags,
    is_current_nav_item,
    resolve_primary_nav_item,
)
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.work.factories import WorkIndexPageFactory


class TestResolvePrimaryNavItem(TestCase):
    def setUp(self):
        root_page = wagtail_factories.PageFactory(parent=None)
        self.home_page = HomePageFactory(parent=root_page)
        self.work_index = WorkIndexPageFactory(parent=self.home_page)
        self.block = PrimaryNavLinkBlock()
        self.site = Site.objects.get(is_default_site=True)

    def test_manual_mixed_list_dropdown(self):
        value = self.block.to_python(
            {
                "page": self.home_page.pk,
                "external_link": "",
                "title": "Services",
                "dropdown_style": "mixed_list",
                "content_source": "manual",
                "main_heading": "Core services",
                "supporting_heading": "Quick start",
                "main_links": [
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
                "supporting_links": [
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

        dropdown = resolve_primary_nav_item(value, self.site)
        self.assertEqual(dropdown["style"], "mixed_list")
        self.assertEqual(dropdown["main_heading"], "Core services")
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertEqual(dropdown["main_items"][0]["text"], "Websites")
        self.assertEqual(len(dropdown["supporting_items"]), 1)

    def test_legacy_streamfield_keys(self):
        """Existing saved nav data uses secondary/promoted keys until re-saved."""
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

        dropdown = resolve_primary_nav_item(value, self.site)
        self.assertEqual(dropdown["main_heading"], "Core services")
        self.assertEqual(dropdown["supporting_heading"], "Quick start")
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertEqual(len(dropdown["supporting_items"]), 1)

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
                "main_heading": "",
                "supporting_heading": "",
                "main_links": [],
                "supporting_links": [],
                "page_children_depth": "2",
            }
        )

        dropdown = resolve_primary_nav_item(value, self.site)
        self.assertEqual(dropdown["style"], "taxonomy_index")
        self.assertEqual(dropdown["main_heading"], "By sector")
        self.assertEqual(dropdown["supporting_heading"], "By service")
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertIn("filter=charities", dropdown["main_items"][0]["url"])
        self.assertIn("filter=seo", dropdown["supporting_items"][0]["url"])

    def test_auto_taxonomy_ignores_manual_supporting_links(self):
        SectorFactory(name="Charities", slug="charities", sort_order=1)
        ServiceFactory(name="SEO", slug="seo", sort_order=1)

        value = self.block.to_python(
            {
                "page": self.work_index.pk,
                "external_link": "",
                "title": "Work",
                "dropdown_style": "taxonomy_index",
                "content_source": "auto_taxonomy",
                "main_heading": "",
                "supporting_heading": "",
                "main_links": [],
                "supporting_links": [
                    {
                        "type": "link",
                        "value": {
                            "page": self.home_page.pk,
                            "external_link": "",
                            "title": "Should be ignored",
                            "description": "Manual override",
                        },
                    }
                ],
                "page_children_depth": "2",
            }
        )

        dropdown = resolve_primary_nav_item(value, self.site)
        self.assertEqual(len(dropdown["supporting_items"]), 1)
        self.assertEqual(dropdown["supporting_items"][0]["text"], "SEO")

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
                "main_heading": "",
                "supporting_heading": "",
                "main_links": [],
                "supporting_links": [],
                "page_children_depth": "1",
            }
        )

        dropdown = resolve_primary_nav_item(value, self.site)
        self.assertIsNotNone(dropdown)
        self.assertEqual(dropdown["style"], "mixed_list")
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertEqual(dropdown["main_items"][0]["text"], "Child page")

    def test_page_children_with_manual_supporting_links(self):
        child = HomePageFactory(parent=self.home_page, title="Child page")
        child.show_in_menus = True
        child.save()

        value = self.block.to_python(
            {
                "page": self.home_page.pk,
                "external_link": "",
                "title": "Thinking",
                "dropdown_style": "mixed_list",
                "content_source": "page_children",
                "main_heading": "Thinking",
                "supporting_heading": "Latest insights",
                "main_links": [],
                "supporting_links": [
                    {
                        "type": "link",
                        "value": {
                            "page": self.home_page.pk,
                            "external_link": "",
                            "title": "Featured article",
                            "description": "Standfirst text",
                        },
                    }
                ],
                "page_children_depth": "1",
            }
        )

        dropdown = resolve_primary_nav_item(value, self.site)
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertEqual(dropdown["main_items"][0]["text"], "Child page")
        self.assertEqual(len(dropdown["supporting_items"]), 1)
        self.assertEqual(dropdown["supporting_items"][0]["text"], "Featured article")

    def test_auto_divisions_with_manual_supporting_links(self):
        value = self.block.to_python(
            {
                "page": self.home_page.pk,
                "external_link": "",
                "title": "Sectors",
                "dropdown_style": "teaser_grid",
                "content_source": "auto_divisions",
                "main_heading": "Sectors we support",
                "supporting_heading": "Our domains",
                "main_links": [],
                "supporting_links": [
                    {
                        "type": "link",
                        "value": {
                            "page": self.home_page.pk,
                            "external_link": "",
                            "title": "Wagtail",
                            "description": "CMS specialists",
                        },
                    }
                ],
                "page_children_depth": "2",
            }
        )

        dropdown = resolve_primary_nav_item(value, self.site)
        self.assertIsNotNone(dropdown)
        self.assertEqual(len(dropdown["supporting_items"]), 1)
        self.assertEqual(dropdown["supporting_items"][0]["text"], "Wagtail")

    def test_no_dropdown_when_style_none(self):
        value = self.block.to_python(
            {
                "page": self.home_page.pk,
                "external_link": "",
                "title": "Home",
                "dropdown_style": "none",
                "content_source": "manual",
                "main_heading": "",
                "supporting_heading": "",
                "main_links": [],
                "supporting_links": [],
                "page_children_depth": "2",
            }
        )

        item = resolve_primary_nav_item(value, self.site)
        self.assertEqual(item["style"], NAV_STYLE_NONE)
        self.assertEqual(item["main_items"], [])
        self.assertEqual(item["supporting_items"], [])
        # Top-level link details are still populated, so templates can render the
        # plain link without falling back to the live block.
        self.assertEqual(item["text"], "Home")
        self.assertEqual(item["page_id"], self.home_page.pk)

    def test_format_nav_tags(self):
        self.assertEqual(format_nav_tags("SEO, PPC"), "SEO · PPC")
        self.assertEqual(format_nav_tags("SEO · PPC"), "SEO · PPC")
        self.assertEqual(format_nav_tags(""), "")


class TestIsCurrentNavItem(TestCase):
    def _item(self, *, url="", page_id=None):
        return {
            "text": "",
            "url": url,
            "page_id": page_id,
            "style": "none",
            "main_heading": "",
            "supporting_heading": "",
            "main_items": [],
            "supporting_items": [],
        }

    def test_returns_true_for_matching_page(self):
        page = SimpleNamespace(pk=1)
        self.assertTrue(
            is_current_nav_item(self._item(url="/about/", page_id=1), page, "/about/")
        )

    def test_returns_true_for_descendant_page(self):
        page = SimpleNamespace(pk=2)
        self.assertTrue(
            is_current_nav_item(
                self._item(url="/about/", page_id=1), page, "/about/team/"
            )
        )

    def test_returns_false_when_item_has_no_url(self):
        page = SimpleNamespace(pk=2)
        self.assertFalse(
            is_current_nav_item(self._item(url="", page_id=1), page, "/home/")
        )

    def test_returns_false_when_current_url_missing_and_pks_differ(self):
        page = SimpleNamespace(pk=2)
        self.assertFalse(
            is_current_nav_item(self._item(url="/about/", page_id=1), page, "")
        )

    def test_returns_false_when_current_page_is_none(self):
        self.assertFalse(
            is_current_nav_item(self._item(url="/about/", page_id=1), None, "/about/")
        )
