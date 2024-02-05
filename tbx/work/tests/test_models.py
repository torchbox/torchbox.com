from tbx.taxonomy.factories import ServiceFactory
from tbx.work.factories import (
    HistoricalWorkPageFactory,
    WorkIndexPageFactory,
    WorkPageFactory,
)
from wagtail.test.utils import WagtailPageTestCase


class TestWorkIndexPageFactory(WagtailPageTestCase):
    def test_create(self):
        WorkIndexPageFactory()


class TestHistoricalWorkPageFactory(WagtailPageTestCase):
    def test_create(self):
        page = HistoricalWorkPageFactory()
        self.assertEqual(page.related_services.count(), 1)

        services = ServiceFactory.create_batch(size=3)
        another_page = HistoricalWorkPageFactory(related_services=list(services))
        self.assertEqual(another_page.related_services.count(), 3)


class TestWorkPageFactory(WagtailPageTestCase):
    def test_create(self):
        page = WorkPageFactory()
        self.assertEqual(page.related_services.count(), 1)

        services = ServiceFactory.create_batch(size=3)
        another_page = WorkPageFactory(related_services=list(services))
        self.assertEqual(another_page.related_services.count(), 3)
