from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import (
    nested_form_data,
    rich_text,
    streamfield,
)

from tbx.core.factories import HomePageFactory, StandardPageFactory
from tbx.core.models import HomePage, StandardPage


class TestHomePageFactory(WagtailPageTestCase):
    def test_create(self):
        HomePageFactory()


class TestStandardPageFactory(WagtailPageTestCase):
    def test_create(self):
        StandardPageFactory()


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
