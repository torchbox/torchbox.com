from django.test import TestCase

from wagtail.models import Page

from tbx.divisions.factories import DivisionPageFactory
from tbx.taxonomy.factories import SectorFactory


class DivisionPageSectorTests(TestCase):
    def test_sector_can_be_assigned(self):
        sector = SectorFactory()
        home = Page.objects.get(slug="home")
        division = DivisionPageFactory(parent=home, title="Charity", sector=sector)
        division.refresh_from_db()
        self.assertEqual(division.sector, sector)

    def test_sector_is_optional(self):
        home = Page.objects.get(slug="home")
        division = DivisionPageFactory(parent=home, title="Charity")
        self.assertIsNone(division.sector)
