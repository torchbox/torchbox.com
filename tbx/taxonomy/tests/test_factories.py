from django.test import TestCase
from django.utils.text import slugify

from tbx.taxonomy.factories import SectorFactory, ServiceFactory, TeamFactory


class ServiceFactoryTestCase(TestCase):
    def test_service_factory(self):
        service = ServiceFactory()
        self.assertIsNotNone(service.name)
        self.assertEqual(service.slug, slugify(service.name))
        self.assertIsNotNone(service.description)
        self.assertIsNotNone(service.sort_order)


class SectorFactoryTestCase(TestCase):
    def test_service_factory(self):
        service = SectorFactory()
        self.assertIsNotNone(service.name)
        self.assertEqual(service.slug, slugify(service.name))
        self.assertIsNotNone(service.description)
        self.assertIsNotNone(service.sort_order)


class TeamFactoryTestCase(TestCase):
    def test_service_factory(self):
        service = TeamFactory()
        self.assertIsNotNone(service.name)
        self.assertEqual(service.slug, slugify(service.name))
        self.assertIsNotNone(service.description)
        self.assertIsNotNone(service.sort_order)
