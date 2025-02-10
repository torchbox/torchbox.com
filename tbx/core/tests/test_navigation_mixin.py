from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.core.factories import HomePageFactory
from tbx.divisions.factories import DivisionPageFactory
from tbx.navigation.factories import NavigationSetFactory
from tbx.services.factories import ServiceAreaPageFactory


class TestNavigationMixin(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Set up the site & homepage.
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.home = HomePageFactory(parent=root)

        site.root_page = cls.home
        site.save()

        # Set up a navigation set.
        cls.nav_set_1 = NavigationSetFactory(name="Charity nav set")
        cls.nav_set_2 = NavigationSetFactory(name="Public sector nav set")

        # Set up a division page.
        cls.division_1 = DivisionPageFactory(
            override_navigation_set=cls.nav_set_1,
            parent=cls.home,
        )
        cls.division_2 = DivisionPageFactory(
            title="Public sector",
            override_navigation_set=cls.nav_set_2,
            parent=cls.home,
        )

        # Set up a services "index" page.
        cls.services = ServiceAreaPageFactory(title="Services", parent=cls.home)
        cls.service_1 = ServiceAreaPageFactory(title="Service 1", parent=cls.services)
        cls.service_2 = ServiceAreaPageFactory(title="Service 2", parent=cls.service_1)

    def test_navigation_set_selected(self):
        """
        For a page that has an override navigation set selected,
        navigation_set should return the selected navigation set.
        """
        self.service_1.override_navigation_set = self.nav_set_1
        self.service_1.save()

        service_3 = ServiceAreaPageFactory(
            override_navigation_set=self.nav_set_2,
            parent=self.service_2,
            title="Service 3",
        )

        self.assertEqual(self.service_1.navigation_set, self.nav_set_1)
        self.assertEqual(service_3.navigation_set, self.nav_set_2)

    def test_navigation_set_selected_on_ancestor(self):
        """
        For a page that does not have a navigation set selected
        but an ancestor page has a navigation set selected,
        navigation_set should return the ancestor's selected navigation set.
        """
        self.service_1.override_navigation_set = self.nav_set_1
        self.service_1.save()

        service_3 = ServiceAreaPageFactory(
            parent=self.service_2,
            title="Service 3",
        )

        self.assertEqual(self.service_1.navigation_set, self.nav_set_1)
        self.assertEqual(self.service_2.navigation_set, self.nav_set_1)
        self.assertEqual(service_3.navigation_set, self.nav_set_1)

    def test_division_with_navigation_set_selected_on_ancestor(self):
        """
        For a page that does not have a navigation set selected
        but an ancestor page has a division with a navigation set selected,
        navigation_set should return that ancestor's selected navigation set.
        """
        self.service_1.division = self.division_2
        self.service_1.save()

        service_3 = ServiceAreaPageFactory(
            parent=self.service_2,
            title="Service 3",
        )
        service_4 = ServiceAreaPageFactory(
            division=self.division_1,
            parent=service_3,
            title="Service 4",
        )
        service_5 = ServiceAreaPageFactory(
            parent=service_4,
            title="Service 5",
        )

        self.assertEqual(self.service_1.navigation_set, self.nav_set_2)
        self.assertEqual(self.service_2.navigation_set, self.nav_set_2)
        self.assertEqual(service_3.navigation_set, self.nav_set_2)
        self.assertEqual(service_4.navigation_set, self.nav_set_1)
        self.assertEqual(service_5.navigation_set, self.nav_set_1)

    def test_no_navigation_set(self):
        """
        For a page that does not have a navigation set selected
        and is not a descendant of a DivisionPage with a navigation set
        nor has an ancestor with a selected navigation set,
        navigation_set should return None.
        """
        service_3 = ServiceAreaPageFactory(
            parent=self.service_2,
            title="Service 3",
        )

        self.assertIsNone(self.service_1.navigation_set)
        self.assertIsNone(self.service_2.navigation_set)
        self.assertIsNone(service_3.navigation_set)
