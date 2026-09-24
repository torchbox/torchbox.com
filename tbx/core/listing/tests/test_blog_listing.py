from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import HomePageFactory
from tbx.core.listing.tests.test_work_listing import (
    SWAP_TARGET_IDS,
    render_listing,
    request_for,
    status_text,
)
from tbx.taxonomy.factories import SectorFactory, ServiceFactory


class BlogListingFilterTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory(title="News")

        cls.charity = SectorFactory(name="Charity", slug="charity")
        cls.health = SectorFactory(name="Health", slug="health")
        cls.design = ServiceFactory(name="Design", slug="design")
        cls.strategy = ServiceFactory(name="Strategy", slug="strategy")

        cls.charity_design = BlogPageFactory(
            title="Charity design",
            parent=cls.index,
            related_sectors=[cls.charity],
            related_services=[cls.design],
        )
        cls.health_strategy = BlogPageFactory(
            title="Health strategy",
            parent=cls.index,
            related_sectors=[cls.health],
            related_services=[cls.strategy],
        )

    def titles(self, params):
        context = self.index.get_context(request_for("/news/", params))
        return {post.title for post in context["blog_posts"]}

    def test_no_filters_shows_everything(self):
        self.assertEqual(self.titles(None), {"Charity design", "Health strategy"})

    def test_sector_filter(self):
        self.assertEqual(self.titles({"sector": ["charity"]}), {"Charity design"})

    def test_service_filter(self):
        self.assertEqual(self.titles({"service": ["strategy"]}), {"Health strategy"})

    def test_or_within_a_filter(self):
        self.assertEqual(
            self.titles({"sector": ["charity", "health"]}),
            {"Charity design", "Health strategy"},
        )

    def test_and_between_filters(self):
        self.assertEqual(
            self.titles({"sector": ["charity"], "service": ["strategy"]}), set()
        )
        self.assertEqual(
            self.titles({"sector": ["health"], "service": ["strategy"]}),
            {"Health strategy"},
        )

    def test_unknown_slug_is_ignored(self):
        self.assertEqual(
            self.titles({"service": ["bogus"]}),
            {"Charity design", "Health strategy"},
        )


class BlogListingMarkupTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        root = Site.objects.get(is_default_site=True).root_page
        home = HomePageFactory(parent=root)
        cls.index = BlogIndexPageFactory(parent=home, title="News")

        cls.charity = SectorFactory(name="Charity", slug="charity")
        cls.health = SectorFactory(name="Health", slug="health")
        cls.design = ServiceFactory(name="Design", slug="design")

        BlogPageFactory(
            title="Charity one",
            parent=cls.index,
            related_sectors=[cls.charity],
            related_services=[cls.design],
        )
        BlogPageFactory(
            title="Charity two", parent=cls.index, related_sectors=[cls.charity]
        )
        BlogPageFactory(
            title="Health one", parent=cls.index, related_sectors=[cls.health]
        )

    def test_swap_targets_are_always_rendered(self):
        for params in ({}, {"sector": "charity"}):
            with self.subTest(params=params):
                soup = render_listing(self, self.index, params)
                for element_id in SWAP_TARGET_IDS:
                    self.assertIsNotNone(soup.find(id=element_id), element_id)

    def test_status_announces_result_count(self):
        cases = (
            ({}, "3 results"),
            ({"sector": "charity"}, "2 results"),
            ({"sector": "health"}, "1 result"),
            ({"sector": "health", "service": "design"}, "0 results"),
        )
        for params, expected in cases:
            with self.subTest(params=params):
                soup = render_listing(self, self.index, params)
                self.assertEqual(status_text(soup), expected)

    def test_pills_identify_the_filter_they_remove(self):
        soup = render_listing(
            self, self.index, {"sector": "charity", "service": "design"}
        )
        pills = soup.select("[data-listing-filters-pill]")
        self.assertEqual(
            [(pill["data-param"], pill["data-value"]) for pill in pills],
            [("sector", "charity"), ("service", "design")],
        )
        self.assertIsNotNone(soup.select_one("[data-listing-filters-clear]"))
