from django.apps import apps
from django.test import TestCase
from django.utils.module_loading import import_string, module_has_submodule

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import (
    nested_form_data,
    rich_text,
    streamfield,
)

from tbx.core.factories import HomePageFactory, StandardPageFactory
from tbx.core.models import HomePage, StandardPage


class TestPageFactory(TestCase):
    """Sanity tests to make sure all pages have a factory."""

    # Exclude these modules from the check.
    # (They currently don't have factories. Un-exclude once they have factories.)
    EXCLUDE = ["tbx.events", "tbx.impact_reports"]

    def test_pages(self):
        app_configs = apps.get_app_configs()
        home_page = HomePageFactory()

        # Create one of every page type using their factory.
        for app in app_configs:
            for model in app.models.values():
                if issubclass(model, Page) and model not in [Page, HomePage]:
                    if app.name in self.EXCLUDE:
                        continue

                    with self.subTest(model=model.__name__):
                        # Get the model's factory
                        self.assertTrue(
                            module_has_submodule(app.module, "factories"),
                            msg=f"App '{app.name}' does not have a factories module.",
                        )

                        page_factory = import_string(
                            f"{app.module.__name__}.factories.{model.__name__}Factory"
                        )

                        page = page_factory(parent=home_page)

                        self.assertIsInstance(page, model)


class TestStandardPage(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.home_page = HomePageFactory(parent=root)

        site.root_page = cls.home_page
        site.save()

        cls.standard_page = StandardPageFactory(
            parent=cls.home_page, title="Test Standard Page"
        )
        cls.standard_page_url = cls.standard_page.url

    def test_can_create_standard_page_under_home_page(self):
        self.assertCanCreateAt(HomePage, StandardPage)

    def test_can_create_standard_page_with_supplied_post_data(self):
        self.login()
        self.assertCanCreate(
            self.home_page,
            StandardPage,
            nested_form_data(
                {
                    "title": "Standard Page",
                    "body": streamfield(
                        [
                            ("h2", "Here's a level 2 heading"),
                            (
                                "paragraph",
                                rich_text("<p>Here's a <em>short</em> paragraph</p>"),
                            ),
                        ]
                    ),
                }
            ),
        )

    def test_standard_page_is_routable(self):
        self.assertPageIsRoutable(self.standard_page)
        self.assertEqual(self.standard_page.url, "/test-standard-page/")

    def test_page_response_media_types(self):
        self.assertEqual(
            self.standard_page.response_media_types, ["text/html", "text/markdown"]
        )

    def test_content_negotiation(self):
        scenarios = [
            # Accept, response content type, has link rel="alternate" in html
            (None, "text/html; charset=utf-8", True),
            ("*/*", "text/html; charset=utf-8", True),
            ("text/*", "text/html; charset=utf-8", True),
            (
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "text/html; charset=utf-8",
                True,
            ),
            ("text/html, text/markdown;q=0.5", "text/html; charset=utf-8", True),
            ("text/markdown;q=0, */*", "text/html; charset=utf-8", True),
            ("text/markdown", "text/markdown; charset=utf-8", False),
            ("text/markdown, text/html;q=0.9", "text/markdown; charset=utf-8", False),
            ("text/markdown, text/html", "text/markdown; charset=utf-8", False),
        ]
        for accept, expected_content_type, is_html in scenarios:
            with self.subTest(accept=accept):
                headers = {"accept": accept} if accept is not None else {}
                response = self.client.get(self.standard_page_url, headers=headers)

                self.assertEqual(
                    response.headers["Content-Type"], expected_content_type
                )
                if is_html:
                    self.assertContains(
                        response,
                        f'<link rel="alternate" type="text/markdown" href="{self.standard_page_url}?format=md" title="Markdown version" />',
                        html=True,
                    )
                else:
                    self.assertNotContains(response, "<!doctype html>")

    def test_page_markdown_variant_via_query_param(self):
        response = self.client.get(
            self.standard_page_url,
            headers={"accept": "text/html"},
            query_params={"format": "md"},
        )
        self.assertEqual(
            response.headers["Content-Type"], "text/markdown; charset=utf-8"
        )
        self.assertNotContains(response, "<!doctype html>")
