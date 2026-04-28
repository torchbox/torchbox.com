from django.core.cache import cache

from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.core.factories import HomePageFactory
from tbx.sitemap.factories import SitemapPageFactory


class TestFooterSitemapLink(WagtailPageTestCase):
    """
    Confirms the Sitemap link appears in the footer when a live SitemapPage
    exists, and is absent when one does not.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.home = HomePageFactory(parent=root)
        site.root_page = cls.home
        site.save()

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_footer_contains_sitemap_link_when_page_exists(self):
        SitemapPageFactory(parent=self.home)
        response = self.client.get(self.home.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/sitemap/"')
        self.assertContains(response, "Sitemap")

    def test_footer_omits_sitemap_link_when_no_page_exists(self):
        response = self.client.get(self.home.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'href="/sitemap/"')
