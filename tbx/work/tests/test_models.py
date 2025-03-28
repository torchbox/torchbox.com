from operator import attrgetter

from django.core.paginator import Page as PaginatorPage

from wagtail.coreutils import get_dummy_request
from wagtail.models import PageViewRestriction, Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.core.factories import HomePageFactory
from tbx.divisions.factories import DivisionPageFactory
from tbx.taxonomy.factories import ServiceFactory
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
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        homepage = HomePageFactory(parent=root)
        division = DivisionPageFactory(parent=homepage, title="Charity")
        work_index = WorkIndexPageFactory(parent=division)

        other_division = DivisionPageFactory(parent=homepage, title="Public")
        other_index = WorkIndexPageFactory(parent=other_division)
        WorkPageFactory(parent=other_index)

        work_page = WorkPageFactory(parent=work_index, title="Work Page 1")
        WorkPageFactory(parent=work_index, title="Work Page 2")
        WorkPageFactory(parent=work_index, title="Work Page 3")

        self.assertQuerySetEqual(
            work_page.related_works,
            [
                "Work Page 2",
                "Work Page 3",
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
