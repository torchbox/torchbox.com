from django.core.exceptions import ValidationError
from django.test import TestCase

from wagtail.models import Page

from tbx.divisions.factories import DivisionPageFactory
from tbx.services.factories import ServicePageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory


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


class DivisionPageServiceTests(TestCase):
    def test_service_can_be_assigned(self):
        service = ServiceFactory()
        home = Page.objects.get(slug="home")
        division = DivisionPageFactory(parent=home, title="Charity", service=service)
        division.refresh_from_db()
        self.assertEqual(division.service, service)

    def test_service_is_optional(self):
        home = Page.objects.get(slug="home")
        division = DivisionPageFactory(parent=home, title="Charity")
        self.assertIsNone(division.service)

    def test_sector_and_service_mutually_exclusive(self):
        sector = SectorFactory()
        service = ServiceFactory()
        home = Page.objects.get(slug="home")
        division = DivisionPageFactory(parent=home, title="Charity")
        division.sector = sector
        division.service = service
        with self.assertRaises(ValidationError):
            division.clean()

    def test_neither_sector_nor_service_is_valid(self):
        home = Page.objects.get(slug="home")
        division = DivisionPageFactory(parent=home, title="Charity")
        division.clean()  # should not raise


class DivisionPageParentPageTests(TestCase):
    def test_can_be_child_of_service_page(self):
        home = Page.objects.get(slug="home")
        service_page = ServicePageFactory(parent=home, title="Engineering")
        division = DivisionPageFactory(parent=service_page, title="Charity")
        self.assertEqual(division.get_parent(), service_page)
