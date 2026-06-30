from django.test import TestCase

from wagtail.models import Page

from tbx.divisions.factories import DivisionPageFactory
from tbx.services.factories import ServiceAreaPageFactory, ServicePageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory


class ServiceAreaPageSectorTests(TestCase):
    def setUp(self):
        home = Page.objects.get(slug="home")
        self.division = DivisionPageFactory(parent=home, title="Division")

    def test_sector_can_be_assigned(self):
        sector = SectorFactory()
        area = ServiceAreaPageFactory(parent=self.division, title="GLAM", sector=sector)
        area.refresh_from_db()
        self.assertEqual(area.sector, sector)

    def test_sector_is_optional(self):
        area = ServiceAreaPageFactory(parent=self.division, title="GLAM")
        self.assertIsNone(area.sector)


class ServicePageServiceTests(TestCase):
    def test_service_can_be_assigned(self):
        service_tag = ServiceFactory()
        home = Page.objects.get(slug="home")
        page = ServicePageFactory(parent=home, title="Design", service=service_tag)
        page.refresh_from_db()
        self.assertEqual(page.service, service_tag)

    def test_service_is_optional(self):
        home = Page.objects.get(slug="home")
        page = ServicePageFactory(parent=home, title="Design")
        self.assertIsNone(page.service)
