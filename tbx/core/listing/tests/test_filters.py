from django.http import QueryDict
from django.test import SimpleTestCase

from tbx.core.listing.filters import (
    EventFilterState,
    TaxonomyFilterState,
    build_listing_seo_context,
    dropdown_is_visible,
    filter_state_for_facet,
    merge_selected_filter_options,
    split_service_filter_options,
    split_service_filter_slugs,
)


class TaxonomyFilterStateTests(SimpleTestCase):
    def test_active_filter_count_and_indexability(self):
        state = TaxonomyFilterState(sectors=("public",), services=("ai", "wagtail"))
        self.assertEqual(state.active_filter_count, 3)
        self.assertTrue(state.has_filters)
        self.assertFalse(state.is_indexable)

    def test_single_filter_is_indexable(self):
        state = TaxonomyFilterState(services=("ai",))
        self.assertTrue(state.is_indexable)

    def test_no_filters_is_not_indexable(self):
        state = TaxonomyFilterState()
        self.assertFalse(state.has_filters)
        self.assertFalse(state.is_indexable)

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

    def test_selected_labels_falls_back_to_slug_for_missing_label(self):
        state = TaxonomyFilterState(
            sectors=("unused-sector",), services=("unused-service",)
        )
        self.assertEqual(
            state.selected_labels(
                sector_labels={},
                service_labels={},
                division_labels={},
            ),
            [
                ("sector", "unused-sector", "unused-sector"),
                ("service", "unused-service", "unused-service"),
            ],
        )


class SplitServiceFilterOptionsTests(SimpleTestCase):
    def test_splits_culture_services_from_main_services(self):
        options = [
            {"value": "ai", "label": "AI"},
            {"value": "culture", "label": "Culture"},
            {"value": "wagtail", "label": "Wagtail"},
            {"value": "sustainability", "label": "Sustainability"},
        ]
        services, culture = split_service_filter_options(options)
        self.assertEqual(
            services,
            [{"value": "ai", "label": "AI"}, {"value": "wagtail", "label": "Wagtail"}],
        )
        self.assertEqual(
            culture,
            [
                {"value": "culture", "label": "Culture"},
                {"value": "sustainability", "label": "Sustainability"},
            ],
        )

    def test_splits_selected_culture_slugs_from_main_service_slugs(self):
        services, culture = split_service_filter_slugs(("ai", "culture", "wagtail"))
        self.assertEqual(services, ("ai", "wagtail"))
        self.assertEqual(culture, ("culture",))


class FacetFilterTests(SimpleTestCase):
    def test_filter_state_for_service_facet_keeps_culture_selections(self):
        state = TaxonomyFilterState(
            sectors=("public-sector",),
            services=("ai", "culture"),
        )
        facet_state = filter_state_for_facet(state, "service")
        self.assertEqual(facet_state.sectors, ("public-sector",))
        self.assertEqual(facet_state.services, ("culture",))

    def test_filter_state_for_culture_facet_keeps_main_service_selections(self):
        state = TaxonomyFilterState(
            sectors=("public-sector",),
            services=("ai", "culture"),
        )
        facet_state = filter_state_for_facet(state, "culture")
        self.assertEqual(facet_state.sectors, ("public-sector",))
        self.assertEqual(facet_state.services, ("ai",))

    def test_filter_state_for_sector_facet_drops_sector_selection(self):
        state = TaxonomyFilterState(sectors=("public-sector",), services=("ai",))
        facet_state = filter_state_for_facet(state, "sector")
        self.assertEqual(facet_state.sectors, ())
        self.assertEqual(facet_state.services, ("ai",))

    def test_unknown_facet_raises(self):
        state = TaxonomyFilterState()
        with self.assertRaises(ValueError):
            filter_state_for_facet(state, "not-a-facet")

    def test_merge_selected_filter_options_keeps_selected_slug(self):
        options = [{"value": "ai", "label": "AI"}]
        merged = merge_selected_filter_options(
            options,
            ("wagtail",),
            {"wagtail": "Wagtail"},
        )
        self.assertEqual(
            merged,
            [{"value": "ai", "label": "AI"}, {"value": "wagtail", "label": "Wagtail"}],
        )


class EventFilterStateTests(SimpleTestCase):
    def test_active_filter_count_and_indexability(self):
        state = EventFilterState(timings=("upcoming",), types=("webinar",))
        self.assertEqual(state.active_filter_count, 2)
        self.assertTrue(state.has_filters)
        self.assertFalse(state.is_indexable)

    def test_single_timing_is_indexable(self):
        state = EventFilterState(timings=("upcoming",))
        self.assertTrue(state.is_indexable)

    def test_both_timings_selected_is_not_indexable(self):
        state = EventFilterState(timings=("upcoming", "past"))
        self.assertEqual(state.active_filter_count, 2)
        self.assertFalse(state.is_indexable)

    def test_no_timings_selected_has_no_filters(self):
        state = EventFilterState()
        self.assertFalse(state.has_filters)

    def test_urlencode_preserves_both_timings(self):
        state = EventFilterState(timings=("upcoming", "past"))
        encoded = state.urlencode()
        self.assertEqual(
            QueryDict(encoded),
            QueryDict("timing=upcoming&timing=past"),
        )

    def test_without_removes_one_timing_keeps_the_other(self):
        state = EventFilterState(timings=("upcoming", "past"))
        updated = state.without(param="timing", slug="upcoming")
        self.assertEqual(updated.timings, ("past",))

    def test_without_removes_type(self):
        state = EventFilterState(types=("webinar", "meetup"))
        updated = state.without(param="type", slug="webinar")
        self.assertEqual(updated.types, ("meetup",))

    def test_selected_labels_only_includes_known_timings(self):
        state = EventFilterState(timings=("upcoming",), types=("webinar",))
        self.assertEqual(
            state.selected_labels(
                type_labels={"webinar": "Webinar"},
                timing_labels={"upcoming": "Upcoming events"},
            ),
            [
                ("timing", "upcoming", "Upcoming events"),
                ("type", "webinar", "Webinar"),
            ],
        )


class ListingSeoContextTests(SimpleTestCase):
    def test_no_filters_uses_plain_title_and_no_robots(self):
        context = build_listing_seo_context(
            page_title="Work",
            filter_labels=[],
            active_filter_count=0,
        )
        self.assertEqual(context["listing_document_title"], "Work")
        self.assertIsNone(context["listing_robots_content"])

    def test_single_filter_title_and_no_robots(self):
        context = build_listing_seo_context(
            page_title="Work",
            filter_labels=["Public sector"],
            active_filter_count=1,
        )
        self.assertEqual(
            context["listing_document_title"], "Work filtered by Public sector"
        )
        self.assertIsNone(context["listing_robots_content"])

    def test_multi_filter_is_noindex(self):
        context = build_listing_seo_context(
            page_title="News",
            filter_labels=["AI", "Public sector"],
            active_filter_count=2,
        )
        self.assertEqual(
            context["listing_document_title"], "News filtered by AI, Public sector"
        )
        self.assertEqual(context["listing_robots_content"], "noindex, nofollow")

    def test_context_only_contains_title_and_robots(self):
        context = build_listing_seo_context(
            page_title="Work",
            filter_labels=[],
            active_filter_count=0,
        )
        self.assertEqual(
            set(context), {"listing_document_title", "listing_robots_content"}
        )


class DropdownIsVisibleTests(SimpleTestCase):
    def test_hides_when_only_option_repeats_dropdown_label(self):
        self.assertFalse(
            dropdown_is_visible(
                [{"value": "culture", "label": "Culture"}], (), "Culture"
            )
        )

    def test_hides_case_insensitively(self):
        self.assertFalse(
            dropdown_is_visible(
                [{"value": "culture", "label": "culture"}], (), "Culture"
            )
        )

    def test_stays_visible_with_two_options(self):
        self.assertTrue(
            dropdown_is_visible(
                [
                    {"value": "culture", "label": "Culture"},
                    {"value": "sustainability", "label": "Sustainability"},
                ],
                (),
                "Culture",
            )
        )

    def test_stays_visible_when_single_option_label_differs(self):
        self.assertTrue(
            dropdown_is_visible([{"value": "ai", "label": "AI"}], (), "Culture")
        )

    def test_stays_visible_when_a_slug_is_already_selected(self):
        self.assertTrue(
            dropdown_is_visible(
                [{"value": "culture", "label": "Culture"}], ("culture",), "Culture"
            )
        )

    def test_hides_when_baseline_has_no_options(self):
        self.assertFalse(dropdown_is_visible([], (), "Sector"))
