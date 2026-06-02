from urllib.parse import urlsplit

from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.blog.factories import BlogIndexPageFactory
from tbx.core.factories import HomePageFactory
from tbx.divisions.factories import DivisionPageFactory


class TestMiddleware(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Set up the site & homepage
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.home = HomePageFactory(parent=root)

        site.root_page = cls.home
        site.save()

        # Set up a division page
        cls.division_page = DivisionPageFactory(
            title="Charity",
            parent=cls.home,
        )

        # Set up a blog page
        cls.blog_page = BlogIndexPageFactory(
            title="Blog",
            parent=cls.division_page,
        )

    def test_page_accessible(self):
        response = self.client.get(self.blog_page.url)
        self.assertEqual(response.status_code, 200)

    def test_redirects_to_lowercase_page(self):
        response = self.client.get(self.blog_page.url.upper())
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, self.blog_page.url)

    def test_maintains_querystring(self):
        response = self.client.get(self.blog_page.url.upper(), {"foo": "BAR"})
        split_result = urlsplit(response.url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(split_result.query, "foo=BAR")

    def test_404(self):
        response = self.client.get("/does-NOT-exist/")
        self.assertEqual(response.status_code, 404)

    def test_redirect(self):
        Redirect.objects.create(
            old_path="/A-redirect", redirect_link="/destination", site=None
        )
        response = self.client.get("/A-redirect/")
        self.assertEqual(response.status_code, 301)

    def test_double_slashed_url_for_missing_page(self):
        response = self.client.get(
            "http://testserver//evil.com"  # Must be a fully-qualified url, as parsing it bypasses the issue we're testing
        )
        self.assertEqual(response.status_code, 404)
