from datetime import timedelta

from django.utils import timezone

from wagtail.blocks.stream_block import StreamValue
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.core.factories import EventTypeFactory, HomePageFactory
from tbx.core.listing.tests.test_work_listing import (
    SWAP_TARGET_IDS,
    render_listing,
    request_for,
    status_text,
)
from tbx.events.factories import EventIndexPageFactory


def event_data(title, event_types, start_date):
    return {
        "type": "event",
        "id": title,
        "value": {
            "title": title,
            "url": [
                {"type": "external_link", "value": "https://example.com", "id": "u"}
            ],
            "type": [event_type.pk for event_type in event_types],
            "location": "",
            "start_date": start_date.isoformat(),
            "start_time": None,
            "end_date": None,
            "end_time": None,
        },
    }


class EventListingFilterTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        root = Site.objects.get(is_default_site=True).root_page
        home = HomePageFactory(parent=root)
        cls.index = EventIndexPageFactory(parent=home)

        cls.webinar = EventTypeFactory(name="Webinar", slug="webinar")
        cls.workshop = EventTypeFactory(name="Workshop", slug="workshop")

        today = timezone.localdate()
        stream_block = cls.index._meta.get_field("events").stream_block
        cls.index.events = StreamValue(
            stream_block,
            [
                event_data(
                    "Upcoming webinar", [cls.webinar], today + timedelta(days=10)
                ),
                event_data(
                    "Upcoming workshop", [cls.workshop], today + timedelta(days=20)
                ),
                event_data("Past webinar", [cls.webinar], today - timedelta(days=10)),
            ],
            is_lazy=True,
        )
        cls.index.save()

    def titles(self, params):
        context = self.index.get_context(request_for("/events/", params))
        return [event.get("title") for event in context["events"]]

    def test_default_shows_upcoming_only(self):
        self.assertEqual(self.titles(None), ["Upcoming webinar", "Upcoming workshop"])

    def test_upcoming_sorted_ascending(self):
        titles = self.titles({"timing": ["upcoming"]})
        self.assertEqual(titles, ["Upcoming webinar", "Upcoming workshop"])

    def test_past_filter(self):
        self.assertEqual(self.titles({"timing": ["past"]}), ["Past webinar"])

    def test_both_timings(self):
        self.assertEqual(
            self.titles({"timing": ["upcoming", "past"]}),
            ["Upcoming webinar", "Upcoming workshop", "Past webinar"],
        )

    def test_type_filter(self):
        self.assertEqual(
            self.titles({"timing": ["upcoming", "past"], "type": ["webinar"]}),
            ["Upcoming webinar", "Past webinar"],
        )

    def test_type_choices_only_used_types(self):
        EventTypeFactory(name="Unused", slug="unused")
        context = self.index.get_context(request_for("/events/"))
        type_dropdown = next(
            d for d in context["filter_dropdowns"] if d["param"] == "type"
        )
        slugs = {option["value"] for option in type_dropdown["options"]}
        self.assertEqual(slugs, {"webinar", "workshop"})

    def test_swap_targets_are_always_rendered(self):
        for params in ({}, {"type": "webinar"}):
            with self.subTest(params=params):
                soup = render_listing(self, self.index, params)
                for element_id in SWAP_TARGET_IDS:
                    self.assertIsNotNone(soup.find(id=element_id), element_id)

    def test_status_announces_result_count(self):
        cases = (
            ({}, "2 results"),
            ({"timing": ["past"]}, "1 result"),
            ({"timing": ["past"], "type": ["workshop"]}, "0 results"),
        )
        for params, expected in cases:
            with self.subTest(params=params):
                soup = render_listing(self, self.index, params)
                self.assertEqual(status_text(soup), expected)
