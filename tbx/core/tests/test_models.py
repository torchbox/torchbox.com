from django.apps import apps
from django.test import TestCase
from django.utils.module_loading import import_string, module_has_submodule

from tbx.core.factories import HomePageFactory, StandardPageFactory
from tbx.core.models import HomePage, StandardPage
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import (
    nested_form_data,
    rich_text,
    streamfield,
)


class TestPageFactory(TestCase):
    """Sanity tests to make sure all pages have a factory."""

    # Exclude these modules from the check.
    # (They currently don't have factories. Un-exclude once they have factories.)
    EXCLUDE = ["tbx.events", "tbx.impact_reports", "tbx.services"]

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
                        assert module_has_submodule(
                            app.module, "factories"
                        ), f"App '{app.name}' does not have a factories module."

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
        standard_page = StandardPageFactory(
            parent=self.home_page, title="Test Standard Page"
        )
        self.assertPageIsRoutable(standard_page)
        self.assertEqual(standard_page.url, "/test-standard-page/")
