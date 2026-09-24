from urllib.parse import urlencode

from wagtail.coreutils import get_dummy_request
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from bs4 import BeautifulSoup

from tbx.core.factories import HomePageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.work.factories import (
    HistoricalWorkPageFactory,
    WorkIndexPageFactory,
    WorkPageFactory,
)


# The listing-filters component swaps these elements in place with HTMX, so
# every listing page must render them, with or without filters selected.
SWAP_TARGET_IDS = (
    "listing-results",
    "listing-pagination",
    "listing-active-filters",
    "listing-status",
)


def request_for(path, params=None):
    query = f"?{urlencode(params, doseq=True)}" if params else ""
    return get_dummy_request(path=f"{path}{query}")


def render_listing(test_case, page, params=None):
    response = test_case.client.get(page.url, params)
    test_case.assertEqual(response.status_code, 200)
    return BeautifulSoup(response.content, "html.parser")


def status_text(soup):
    return " ".join(soup.find(id="listing-status").get_text().split())


class WorkListingFilterTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.index = WorkIndexPageFactory(title="Our work")

        cls.charity = SectorFactory(name="Charity", slug="charity")
        cls.health = SectorFactory(name="Health", slug="health")
        cls.design = ServiceFactory(name="Design", slug="design")
        cls.strategy = ServiceFactory(name="Strategy", slug="strategy")

        cls.work_charity_design = WorkPageFactory(
            title="Charity design", parent=cls.index, related_services=[cls.design]
        )
        cls.work_charity_design.related_sectors.add(cls.charity)
        cls.work_charity_design.save()

        cls.work_health_strategy = WorkPageFactory(
            title="Health strategy", parent=cls.index, related_services=[cls.strategy]
        )
        cls.work_health_strategy.related_sectors.add(cls.health)
        cls.work_health_strategy.save()

        cls.historical_charity_design = HistoricalWorkPageFactory(
            title="Historical charity design",
            parent=cls.index,
            related_services=[cls.design],
        )
        cls.historical_charity_design.related_sectors.add(cls.charity)
        cls.historical_charity_design.save()

    def titles(self, params):
        context = self.index.get_context(request_for("/our-work/", params))
        return {work["title"] for work in context["works"]}

    def test_no_filters_shows_everything(self):
        self.assertEqual(
            self.titles(None),
            {"Charity design", "Health strategy", "Historical charity design"},
        )

    def test_sector_filter_matches_both_subtypes(self):
        self.assertEqual(
            self.titles({"sector": ["charity"]}),
            {"Charity design", "Historical charity design"},
        )

    def test_service_filter_matches_both_subtypes(self):
        self.assertEqual(
            self.titles({"service": ["design"]}),
            {"Charity design", "Historical charity design"},
        )

    def test_or_within_a_filter(self):
        self.assertEqual(
            self.titles({"sector": ["charity", "health"]}),
            {"Charity design", "Health strategy", "Historical charity design"},
        )

    def test_and_between_filters(self):
        # Charity work is all Design, so charity + strategy matches nothing.
        self.assertEqual(
            self.titles({"sector": ["charity"], "service": ["strategy"]}), set()
        )
        self.assertEqual(
            self.titles({"sector": ["charity"], "service": ["design"]}),
            {"Charity design", "Historical charity design"},
        )

    def test_unknown_slug_is_ignored(self):
        self.assertEqual(
            self.titles({"sector": ["bogus"]}),
            {"Charity design", "Health strategy", "Historical charity design"},
        )

    def test_dropdown_options_only_include_used_terms(self):
        SectorFactory(name="Unused", slug="unused")
        context = self.index.get_context(request_for("/our-work/"))
        sector_dropdown = next(
            d for d in context["filter_dropdowns"] if d["param"] == "sector"
        )
        slugs = {option["value"] for option in sector_dropdown["options"]}
        self.assertEqual(slugs, {"charity", "health"})

    def test_pagination_keeps_filters(self):
        for index in range(11):
            page = WorkPageFactory(
                title=f"Extra charity {index}",
                parent=self.index,
                related_services=[self.design],
            )
            page.related_sectors.add(self.charity)
            page.save()

        context = self.index.get_context(
            request_for("/our-work/", {"sector": ["charity"], "page": "2"})
        )
        self.assertIn("sector=charity", context["extra_url_params"])
        self.assertEqual(context["works"].number, 2)


class WorkListingMarkupTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        root = Site.objects.get(is_default_site=True).root_page
        home = HomePageFactory(parent=root)
        cls.index = WorkIndexPageFactory(parent=home, title="Our work")

        cls.charity = SectorFactory(name="Charity", slug="charity")
        cls.health = SectorFactory(name="Health", slug="health")
        cls.design = ServiceFactory(name="Design", slug="design")

        for title, sector in (
            ("Charity one", cls.charity),
            ("Charity two", cls.charity),
            ("Health one", cls.health),
        ):
            work = WorkPageFactory(
                title=title, parent=cls.index, related_services=[cls.design]
            )
            work.related_sectors.add(sector)
            work.save()

    def test_swap_targets_are_always_rendered(self):
        for params in ({}, {"sector": "charity"}):
            with self.subTest(params=params):
                soup = render_listing(self, self.index, params)
                for element_id in SWAP_TARGET_IDS:
                    self.assertIsNotNone(soup.find(id=element_id), element_id)

    def test_status_announces_result_count(self):
        cases = (
            ({}, "3 results"),
            ({"sector": "charity"}, "2 results"),
            ({"sector": "health"}, "1 result"),
        )
        for params, expected in cases:
            with self.subTest(params=params):
                soup = render_listing(self, self.index, params)
                self.assertEqual(status_text(soup), expected)
