from operator import attrgetter

from django.core.paginator import Page as PaginatorPage

from wagtail.coreutils import get_dummy_request
from wagtail.models import PageViewRestriction
from wagtail.test.utils import WagtailPageTestCase

from wagtail_factories import PageFactory

from tbx.divisions.factories import DivisionPageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.work.factories import (
    HistoricalWorkPageFactory,
    WorkIndexPageFactory,
    WorkPageFactory,
)
from tbx.work.models import WorkPage


class TestWorkIndexPageFactory(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.work_index = WorkIndexPageFactory(title="Our work")
        cls.work_page = WorkPageFactory(title="Work page", parent=cls.work_index)
        cls.private_work_page = WorkPageFactory(
            title="Private work page", parent=cls.work_index
        )
        cls.draft_work_page = WorkPageFactory(
            title="Draft work page", live=False, parent=cls.work_index
        )
        PageViewRestriction.objects.create(
            page=cls.private_work_page,
            restriction_type="password",
            password="password123",  # noqa: S106
        )

    def test_get_context(self):
        context = self.work_index.get_context(get_dummy_request())
        work_pages = context["works"]
        self.assertIsInstance(work_pages, PaginatorPage)
        self.assertEqual(work_pages[0]["title"], self.work_page.title)

    def test_works_property(self):
        """Checks that the works property returns public and published work pages under the given work index."""
        another_work_index = WorkIndexPageFactory(title="Another work index")
        WorkPageFactory(title="Another work page", parent=another_work_index)
        self.assertQuerySetEqual(
            self.work_index.works, WorkPage.objects.filter(pk=self.work_page.pk)
        )


class TestHistoricalWorkPageFactory(WagtailPageTestCase):
    def test_create(self):
        page = HistoricalWorkPageFactory()
        self.assertEqual(page.related_services.count(), 1)

        services = ServiceFactory.create_batch(size=3)
        another_page = HistoricalWorkPageFactory(related_services=list(services))
        self.assertEqual(another_page.related_services.count(), 3)


class TestWorkPage(WagtailPageTestCase):
    def test_related_works(self):
        sector = SectorFactory.create()
        # The logic of `final_division` skips ancestors with depth <= 2,
        # So we create the division page with enough parents to be at depth 3:
        division = DivisionPageFactory.create(parent=PageFactory(parent=PageFactory()))
        work_page = WorkPageFactory(division=division, related_sectors=[sector])
        WorkPageFactory(title="same sector", division=None, related_sectors=[sector])
        WorkPageFactory(
            title="same division (direct)", division=division, related_sectors=[]
        )
        WorkPageFactory(
            title="same division (direct) same sector",
            division=division,
            related_sectors=[sector],
        )
        WorkPageFactory(title="same division (parent)", parent=division)

        self.assertQuerySetEqual(
            work_page.related_works,
            [
                "same division (direct)",
                "same division (direct) same sector",
                "same division (parent)",
            ],
            transform=attrgetter("title"),
            ordered=False,
        )


class TestWorkPageFactory(WagtailPageTestCase):
    def test_create(self):
        page = WorkPageFactory()
        self.assertEqual(page.related_services.count(), 1)

        services = ServiceFactory.create_batch(size=3)
        another_page = WorkPageFactory(related_services=list(services))
        self.assertEqual(another_page.related_services.count(), 3)
