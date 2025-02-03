from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.core.factories import HomePageFactory
from tbx.divisions.factories import DivisionPageFactory
from tbx.services.factories import ServiceAreaPageFactory


class TestDivisionMixin(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Set up the site & homepage.
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.home = HomePageFactory(parent=root)

        site.root_page = cls.home
        site.save()

        # Set up a services "index" page.
        cls.services = ServiceAreaPageFactory(title="Services", parent=cls.home)
        cls.service_1 = ServiceAreaPageFactory(title="Service 1", parent=cls.services)
        cls.service_2 = ServiceAreaPageFactory(title="Service 2", parent=cls.service_1)

        # Set up a division page.
        cls.division_1 = DivisionPageFactory(parent=cls.home)
        cls.division_2 = DivisionPageFactory(title="Public sector", parent=cls.home)

    def test_division_selected(self):
        """
        For a page that has division selected,
        final_division should return the selected page.
        """
        self.service_1.division = self.division_1
        self.service_1.save()

        service_3 = ServiceAreaPageFactory(
            division=self.division_2,
            parent=self.service_2,
            title="Service 3",
        )

        self.assertEqual(self.service_1.final_division, self.division_1)
        self.assertEqual(service_3.final_division, self.division_2)

    def test_division_selected_on_ancestor(self):
        """
        For a page that does not have a division selected
        but an ancestor page has a division selected,
        final_division should return the ancestor's selected page.
        """
        self.service_1.division = self.division_1
        self.service_1.save()

        service_3 = ServiceAreaPageFactory(
            parent=self.service_2,
            title="Service 3",
        )

        self.assertEqual(self.service_1.final_division, self.division_1)
        self.assertEqual(self.service_2.final_division, self.division_1)
        self.assertEqual(service_3.final_division, self.division_1)

    def test_division_as_ancestor(self):
        """
        For a page that does not have a division selected
        but an ancestor page is a DivisionPage,
        final_division should return the ancestor DivisionPage.
        """
        service_a = ServiceAreaPageFactory(
            title="Service A",
            parent=self.division_1,
        )
        service_b = ServiceAreaPageFactory(
            title="Service A",
            parent=service_a,
        )

        self.assertEqual(service_a.final_division, self.division_1)
        self.assertEqual(service_b.final_division, self.division_1)

    def test_no_division(self):
        """
        For a page that does not have a division selected
        and is not a descendant of a DivisionPage
        nor has an ancestor with a selected division,
        final_division should return None.
        """
        service_3 = ServiceAreaPageFactory(
            parent=self.service_2,
            title="Service 3",
        )

        self.assertIsNone(self.service_1.final_division)
        self.assertIsNone(self.service_2.final_division)
        self.assertIsNone(service_3.final_division)
