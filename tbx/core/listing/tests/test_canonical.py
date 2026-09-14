from datetime import timedelta
from urllib.parse import urlencode

from django.test import SimpleTestCase
from django.utils import timezone

from wagtail.blocks.stream_block import StreamValue
from wagtail.coreutils import get_dummy_request
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from bs4 import BeautifulSoup

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import EventTypeFactory, HomePageFactory
from tbx.core.listing.context import build_listing_filter_context
from tbx.core.listing.forms import EventFilterForm, TaxonomyFilterForm
from tbx.events.factories import EventIndexPageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.work.factories import WorkIndexPageFactory, WorkPageFactory


def request_for(params=None):
    query = f"?{urlencode(params, doseq=True)}" if params else ""
    return get_dummy_request(path=f"/listing/{query}")


class ListingCanonicalQueryStringTests(SimpleTestCase):
    taxonomy_choices = {
        "sector_choices": [("charity", "Charity"), ("health", "Health")],
        "service_choices": [
            ("design", "Design"),
            ("strategy", "Strategy"),
            ("charity", "Charity service"),
        ],
    }
    taxonomy_dropdowns = (("sector", "Sector"), ("service", "Service"))

    def canonical_query_string(
        self, params, form_class=TaxonomyFilterForm, dropdowns=None, **kwargs
    ):
        request = request_for(params)
        form = form_class(request.GET, **kwargs)
        self.assertTrue(form.is_valid())
        return build_listing_filter_context(
            request,
            form,
            dropdowns or self.taxonomy_dropdowns,
        )["canonical_query_string"]

    def test_keeps_one_taxonomy_filter(self):
        cases = (
            ({"sector": "charity"}, "sector=charity"),
            ({"service": "design"}, "service=design"),
        )

        for params, expected in cases:
            with self.subTest(params=params):
                self.assertEqual(
                    self.canonical_query_string(params, **self.taxonomy_choices),
                    expected,
                )

    def test_drops_multiple_taxonomy_filters(self):
        cases = (
            {"sector": ["charity", "health"]},
            {"sector": "charity", "service": "design"},
            {"sector": "charity", "service": "charity"},
        )

        for params in cases:
            with self.subTest(params=params):
                self.assertEqual(
                    self.canonical_query_string(params, **self.taxonomy_choices), ""
                )

    def test_ignores_unknown_filters_and_unrelated_parameters(self):
        self.assertEqual(
            self.canonical_query_string(
                {
                    "sector": ["unknown", "charity"],
                    "filter": "legacy",
                    "utm_source": "newsletter",
                },
                **self.taxonomy_choices,
            ),
            "sector=charity",
        )

    def test_pagination_excludes_filters(self):
        cases = (
            ({"page": "2"}, "page=2"),
            ({"page": "2 & more"}, "page=2+%26+more"),
            ({"sector": "charity", "page": "2"}, "page=2"),
            (
                {"sector": ["charity", "health"], "page": "2"},
                "page=2",
            ),
        )

        for params, expected in cases:
            with self.subTest(params=params):
                self.assertEqual(
                    self.canonical_query_string(params, **self.taxonomy_choices),
                    expected,
                )

    def test_keeps_one_event_filter(self):
        dropdowns = (("timing", "When"), ("type", "Event type"))
        cases = (
            ({"timing": "past"}, "timing=past"),
            ({"type": "webinar"}, "type=webinar"),
        )

        for params, expected in cases:
            with self.subTest(params=params):
                self.assertEqual(
                    self.canonical_query_string(
                        params,
                        form_class=EventFilterForm,
                        dropdowns=dropdowns,
                        type_choices=[("webinar", "Webinar")],
                    ),
                    expected,
                )


def event_data(title, event_types, start_date):
    return {
        "type": "event",
        "id": title,
        "value": {
            "title": title,
            "url": [
                {
                    "type": "external_link",
                    "value": "https://example.com",
                    "id": "url",
                }
            ],
            "type": [event_type.pk for event_type in event_types],
            "location": "",
            "start_date": start_date.isoformat(),
            "start_time": None,
            "end_date": None,
            "end_time": None,
        },
    }


class ListingCanonicalTagTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        root = Site.objects.get(is_default_site=True).root_page
        cls.home = HomePageFactory(parent=root)
        cls.blog_index = BlogIndexPageFactory(parent=cls.home, title="News")
        cls.work_index = WorkIndexPageFactory(parent=cls.home, title="Our work")
        cls.event_index = EventIndexPageFactory(parent=cls.home, title="Events")

        cls.charity = SectorFactory(name="Charity", slug="charity")
        cls.health = SectorFactory(name="Health", slug="health")
        cls.design = ServiceFactory(name="Design", slug="design")

        for index in range(11):
            BlogPageFactory(
                parent=cls.blog_index,
                title=f"Charity article {index}",
                related_sectors=[cls.charity],
                related_services=[cls.design],
            )
        BlogPageFactory(
            parent=cls.blog_index,
            title="Health article",
            related_sectors=[cls.health],
        )

        cls.canonical_blog_page = BlogPageFactory(
            parent=cls.blog_index,
            title="Canonical article",
            canonical_url="https://example.com/preferred/",
        )

        work = WorkPageFactory(
            parent=cls.work_index,
            title="Charity work",
            related_services=[cls.design],
        )
        work.related_sectors.add(cls.charity)
        work.save()

        cls.webinar = EventTypeFactory(name="Webinar", slug="webinar")
        cls.conference = EventTypeFactory(name="Conference", slug="conference")
        today = timezone.localdate()
        stream_block = cls.event_index._meta.get_field("events").stream_block
        cls.event_index.events = StreamValue(
            stream_block,
            [
                event_data(
                    "Upcoming webinar", [cls.webinar], today + timedelta(days=10)
                ),
                event_data(
                    "Past conference", [cls.conference], today - timedelta(days=10)
                ),
            ],
            is_lazy=True,
        )
        cls.event_index.save()

    def assert_canonical(self, page, params, expected):
        response = self.client.get(page.url, params)
        self.assertEqual(response.status_code, 200)
        canonical_tags = BeautifulSoup(response.content, "html.parser").select(
            'link[rel="canonical"]'
        )
        self.assertEqual(len(canonical_tags), 1)
        self.assertEqual(canonical_tags[0]["href"], expected)

    def test_listing_filter_canonicals(self):
        cases = (
            (self.blog_index, {}, self.blog_index.full_url),
            (
                self.blog_index,
                {"sector": "charity"},
                f"{self.blog_index.full_url}?sector=charity",
            ),
            (
                self.blog_index,
                {"sector": "charity", "service": "design"},
                self.blog_index.full_url,
            ),
            (self.work_index, {}, self.work_index.full_url),
            (
                self.work_index,
                {"sector": "charity"},
                f"{self.work_index.full_url}?sector=charity",
            ),
            (
                self.work_index,
                {"sector": "charity", "service": "design"},
                self.work_index.full_url,
            ),
            (self.event_index, {}, self.event_index.full_url),
            (
                self.event_index,
                {"type": "webinar"},
                f"{self.event_index.full_url}?type=webinar",
            ),
            (
                self.event_index,
                {"timing": "past", "type": "conference"},
                self.event_index.full_url,
            ),
        )

        for page, params, expected in cases:
            with self.subTest(page=page, params=params):
                self.assert_canonical(page, params, expected)

    def test_paginated_canonicals(self):
        cases = (
            (
                {"sector": "charity", "page": "2"},
                f"{self.blog_index.full_url}?page=2",
            ),
            (
                {"sector": "charity", "service": "design", "page": "2"},
                f"{self.blog_index.full_url}?page=2",
            ),
            ({"page": "2"}, f"{self.blog_index.full_url}?page=2"),
        )

        for params, expected in cases:
            with self.subTest(params=params):
                self.assert_canonical(self.blog_index, params, expected)

    def test_valid_filter_is_kept_when_there_are_no_results(self):
        self.assert_canonical(
            self.event_index,
            {"type": "conference"},
            f"{self.event_index.full_url}?type=conference",
        )

    def test_unsupported_parameters_are_omitted(self):
        cases = (
            (self.blog_index, {"filter": "charity"}, self.blog_index.full_url),
            (
                self.blog_index,
                {"filter": "legacy", "sector": "charity"},
                f"{self.blog_index.full_url}?sector=charity",
            ),
            (self.work_index, {"filter": "charity"}, self.work_index.full_url),
        )

        for page, params, expected in cases:
            with self.subTest(page=page, params=params):
                self.assert_canonical(page, params, expected)

    def test_editor_canonical_url_takes_precedence(self):
        self.assert_canonical(
            self.canonical_blog_page,
            {"sector": "charity", "page": "2"},
            "https://example.com/preferred/",
        )
