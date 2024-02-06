from django.test import TestCase
from django.utils.text import slugify

from tbx.taxonomy.factories import ServiceFactory


class ServiceFactoryTestCase(TestCase):
    def test_service_factory(self):
        service = ServiceFactory()
        self.assertIsNotNone(service.name)
        self.assertEqual(service.slug, slugify(service.name))
        self.assertIsNotNone(service.description)
        self.assertIsNotNone(service.sort_order)
