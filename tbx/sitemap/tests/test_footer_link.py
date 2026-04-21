from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.core.factories import HomePageFactory


class TestFooterSitemapLink(WagtailPageTestCase):
    """
    Confirms the hardcoded Sitemap link is present in the footer on every page.
    The link is hardcoded rather than CMS-managed so editors cannot remove it
    via the admin. This test guards that invariant.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.home = HomePageFactory(parent=root)
        site.root_page = cls.home
        site.save()

    def test_footer_contains_sitemap_link(self):
        response = self.client.get(self.home.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/sitemap/"')
        self.assertContains(response, "Sitemap")
