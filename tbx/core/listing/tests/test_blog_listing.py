from wagtail.test.utils import WagtailPageTestCase

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.listing.tests.test_work_listing import request_for
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
