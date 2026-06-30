from django.test import TestCase

from wagtail.models import Page

from tbx.sectors.factories import SectorsIndexPageFactory
from tbx.sectors.models import SectorsIndexPage


class SectorsIndexPageTests(TestCase):
    def test_can_create_under_home(self):
        home = Page.objects.get(slug="home")
        page = SectorsIndexPageFactory(parent=home, title="Sectors")
        self.assertIsInstance(page, SectorsIndexPage)
        self.assertEqual(page.get_parent().specific_class, type(home.specific))

    def test_allows_division_and_service_area_children(self):
        from tbx.divisions.models import DivisionPage
        from tbx.services.models import ServiceAreaPage

        allowed = {cls.__name__ for cls in SectorsIndexPage.allowed_subpage_models()}
        self.assertIn(DivisionPage.__name__, allowed)
        self.assertIn(ServiceAreaPage.__name__, allowed)

    def test_division_page_can_be_created_under_index(self):
        from tbx.divisions.factories import DivisionPageFactory

        home = Page.objects.get(slug="home")
        index = SectorsIndexPageFactory(parent=home, title="Sectors")
        division = DivisionPageFactory(parent=index, title="Charity")
        self.assertEqual(division.get_parent().specific, index)

    def test_service_area_page_can_be_created_under_index(self):
        from tbx.services.factories import ServiceAreaPageFactory

        home = Page.objects.get(slug="home")
        index = SectorsIndexPageFactory(parent=home, title="Sectors")
        area = ServiceAreaPageFactory(parent=index, title="GLAM")
        self.assertEqual(area.get_parent().specific, index)
