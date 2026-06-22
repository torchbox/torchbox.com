from django.http import QueryDict
from django.test import SimpleTestCase

from tbx.core.listing.filters import (
    EventFilterState,
    TaxonomyFilterState,
    build_listing_seo_context,
    get_listing_paths,
)


class GetListingPathsTests(SimpleTestCase):
    def test_uses_request_host_for_absolute_url(self):
        class Page:
            def get_url(self, request):
                return "/public-sector/work/"

        request = type(
            "Request",
            (),
            {
                "build_absolute_uri": lambda self, path: f"http://localhost:8000{path}",
            },
        )()

        listing_path, absolute_url = get_listing_paths(Page(), request)
        self.assertEqual(listing_path, "/public-sector/work/")
        self.assertEqual(absolute_url, "http://localhost:8000/public-sector/work/")


class TaxonomyFilterStateTests(SimpleTestCase):
    def test_parses_multiple_params(self):
        request = self._request({"sector": ["public"], "service": ["ai", "wagtail"]})
        state = TaxonomyFilterState.from_request(
            request,
            valid_sector_slugs={"public"},
            valid_service_slugs={"ai", "wagtail"},
            valid_division_slugs=set(),
        )
        self.assertEqual(state.sectors, ("public",))
        self.assertEqual(state.services, ("ai", "wagtail"))
        self.assertEqual(state.active_filter_count, 3)
        self.assertFalse(state.is_indexable)

    def test_legacy_filter_param_maps_to_taxonomy(self):
        request = self._request({"filter": ["ai"]})
        state = TaxonomyFilterState.from_request(
            request,
            valid_sector_slugs=set(),
            valid_service_slugs={"ai"},
            valid_division_slugs=set(),
        )
        self.assertEqual(state.services, ("ai",))
        self.assertTrue(state.is_indexable)

    def test_urlencode_preserves_repeated_params(self):
        state = TaxonomyFilterState(sectors=("public",), services=("ai", "wagtail"))
        encoded = state.urlencode()
        self.assertEqual(
            QueryDict(encoded),
            QueryDict("sector=public&service=ai&service=wagtail"),
        )

    def test_without_removes_selected_filter(self):
        state = TaxonomyFilterState(services=("ai", "wagtail"), sectors=("public",))
        updated = state.without(param="service", slug="ai")
        self.assertEqual(updated.services, ("wagtail",))
        self.assertEqual(updated.sectors, ("public",))

    def _request(self, params):
        class Request:
            GET = QueryDict("", mutable=True)

        request = Request()
        for key, values in params.items():
            for value in values:
                request.GET.appendlist(key, value)
        return request


class EventFilterStateTests(SimpleTestCase):
    def test_legacy_past_filter(self):
        class Request:
            GET = QueryDict("filter=past")

        state = EventFilterState.from_request(Request(), valid_type_slugs=set())
        self.assertEqual(state.timing, "past")

    def test_multiple_types_not_indexable(self):
        class Request:
            GET = QueryDict("type=webinar&type=meetup")

        state = EventFilterState.from_request(
            Request(),
            valid_type_slugs={"webinar", "meetup"},
        )
        self.assertEqual(state.active_filter_count, 2)
        self.assertFalse(state.is_indexable)


class ListingSeoContextTests(SimpleTestCase):
    def test_single_filter_title_and_canonical(self):
        context = build_listing_seo_context(
            page_title="Work",
            filter_labels=["Public sector"],
            active_filter_count=1,
            base_url="https://torchbox.com/work/",
            current_url="https://torchbox.com/work/?sector=public",
            has_page_param=False,
        )
        self.assertEqual(context["listing_document_title"], "Work filtered by Public sector")
        self.assertIsNone(context["listing_robots_content"])
        self.assertEqual(
            context["listing_canonical_url"],
            "https://torchbox.com/work/?sector=public",
        )

    def test_multi_filter_is_noindex(self):
        context = build_listing_seo_context(
            page_title="News",
            filter_labels=["AI", "Public sector"],
            active_filter_count=2,
            base_url="https://torchbox.com/news/",
            current_url="https://torchbox.com/news/?service=ai&sector=public",
            has_page_param=False,
        )
        self.assertEqual(context["listing_robots_content"], "noindex, nofollow")
        self.assertEqual(context["listing_canonical_url"], "https://torchbox.com/news/")

    def test_paginated_unfiltered_canonicalises_to_base(self):
        context = build_listing_seo_context(
            page_title="Work",
            filter_labels=[],
            active_filter_count=0,
            base_url="https://torchbox.com/work/",
            current_url="https://torchbox.com/work/?page=2",
            has_page_param=True,
        )
        self.assertEqual(context["listing_canonical_url"], "https://torchbox.com/work/")
