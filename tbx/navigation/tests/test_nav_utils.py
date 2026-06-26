from types import SimpleNamespace

from django.test import TestCase

from wagtail.models import Site

import wagtail_factories

from tbx.core.factories import HomePageFactory
from tbx.navigation.blocks import PrimaryNavLinkBlock
from tbx.navigation.utils import (
    format_nav_tags,
    primary_nav_item_is_current,
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

        dropdown = resolve_primary_nav_dropdown(value, self.site)
        self.assertEqual(dropdown["style"], "mixed_list")
        self.assertEqual(dropdown["main_heading"], "Core services")
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertEqual(dropdown["main_items"][0].text, "Websites")
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

        dropdown = resolve_primary_nav_dropdown(value, self.site)
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

        dropdown = resolve_primary_nav_dropdown(value, self.site)
        self.assertEqual(dropdown["style"], "taxonomy_index")
        self.assertEqual(dropdown["main_heading"], "By sector")
        self.assertEqual(dropdown["supporting_heading"], "By service")
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertIn("filter=charities", dropdown["main_items"][0].url)
        self.assertIn("filter=seo", dropdown["supporting_items"][0].url)

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

        dropdown = resolve_primary_nav_dropdown(value, self.site)
        self.assertEqual(len(dropdown["supporting_items"]), 1)
        self.assertEqual(dropdown["supporting_items"][0].text, "SEO")

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

        dropdown = resolve_primary_nav_dropdown(value, self.site)
        self.assertIsNotNone(dropdown)
        self.assertEqual(dropdown["style"], "mixed_list")
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertEqual(dropdown["main_items"][0].text, "Child page")

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

        dropdown = resolve_primary_nav_dropdown(value, self.site)
        self.assertEqual(len(dropdown["main_items"]), 1)
        self.assertEqual(dropdown["main_items"][0].text, "Child page")
        self.assertEqual(len(dropdown["supporting_items"]), 1)
        self.assertEqual(dropdown["supporting_items"][0].text, "Featured article")

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

        dropdown = resolve_primary_nav_dropdown(value, self.site)
        self.assertIsNotNone(dropdown)
        self.assertEqual(len(dropdown["supporting_items"]), 1)
        self.assertEqual(dropdown["supporting_items"][0].text, "Wagtail")

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

        self.assertIsNone(resolve_primary_nav_dropdown(value, self.site))

    def test_format_nav_tags(self):
        self.assertEqual(format_nav_tags("SEO, PPC"), "SEO · PPC")
        self.assertEqual(format_nav_tags("SEO · PPC"), "SEO · PPC")
        self.assertEqual(format_nav_tags(""), "")


class TestPrimaryNavItemIsCurrent(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)

    def _nav_item(self, page):
        return SimpleNamespace(
            get=lambda key, default=None: page if key == "page" else default
        )

    def test_returns_true_for_matching_page(self):
        page = SimpleNamespace(pk=1, url="/about/")
        self.assertTrue(
            primary_nav_item_is_current(self._nav_item(page), page, self.site)
        )

    def test_returns_true_for_descendant_page(self):
        section = SimpleNamespace(pk=1, url="/about/")
        child = SimpleNamespace(pk=2, url="/about/team/")
        self.assertTrue(
            primary_nav_item_is_current(self._nav_item(section), child, self.site)
        )

    def test_returns_false_when_nav_page_has_no_url(self):
        section = SimpleNamespace(pk=1, url=None)
        current = SimpleNamespace(pk=2, url="/home/")
        self.assertFalse(
            primary_nav_item_is_current(self._nav_item(section), current, self.site)
        )

    def test_returns_false_when_current_page_has_no_url(self):
        section = SimpleNamespace(pk=1, url="/about/")
        current = SimpleNamespace(pk=2, url=None)
        self.assertFalse(
            primary_nav_item_is_current(self._nav_item(section), current, self.site)
        )

    def test_returns_false_when_no_nav_page(self):
        current = SimpleNamespace(pk=1, url="/home/")
        item = SimpleNamespace(get=lambda key, default=None: default)
        self.assertFalse(primary_nav_item_is_current(item, current, self.site))
