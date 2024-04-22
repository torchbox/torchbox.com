from django.utils.text import slugify

from bs4 import BeautifulSoup
from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import HomePageFactory, StandardPageFactory
from tbx.core.utils.models import ColourTheme
from tbx.work.factories import (
    HistoricalWorkPageFactory,
    WorkIndexPageFactory,
    WorkPageFactory,
)
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase


class TestNavigationText(WagtailPageTestCase):
    def setUp(self):
        super().setUp()

        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        self.home = HomePageFactory(parent=root)

        site.root_page = self.home
        site.save()

        self.standard_page = StandardPageFactory(title="Test standard page", parent=self.home)

    def test_override(self):
        self.standard_page.navigation_text = "Test navigation override text"

        self.assertEqual(self.standard_page.nav_text, "Test navigation override text")

    def test_no_override(self):
        self.assertEqual(self.standard_page.nav_text, "Test standard page")
