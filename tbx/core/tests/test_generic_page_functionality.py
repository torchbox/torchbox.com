from django.test import SimpleTestCase
from tbx.core.models import StandardPage


class TestNavigationText(SimpleTestCase):
    def test_nav_text_prefers_navigation_text(self):
        page = StandardPage(id=1, title="Title", navigation_text="Navigation text")
        self.assertEqual(page.nav_text, "Navigation text")

    def test_nav_text_uses_page_title_as_fallback(self):
        page = StandardPage(id=1, title="Title", navigation_text="")
        self.assertEqual(page.nav_text, "Title")
