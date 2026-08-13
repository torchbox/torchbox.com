import datetime
import re

from django.utils import timezone

from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.core.factories import HomePageFactory
from tbx.core.listing.tests import reset_site_root_paths
from tbx.core.models import EventType
from tbx.events.models import EventIndexPage


def _event(*, title, event_type, start_date):
    """Build a single StreamField `event` block's raw value.

    There's no factory for `EventItemBlock` anywhere in the repo (its `type` field
    is a `ListBlock` of snippet choosers and its `url` field is a required
    `StreamBlock`), so this constructs the raw value directly the same way
    assigning to a StreamField attribute in a shell would.
    """
    return (
        "event",
        {
            "title": title,
            "url": [("external_link", "https://example.com")],
            "type": [event_type],
            "location": "",
            "start_date": start_date,
            "start_time": None,
            "end_date": None,
            "end_time": None,
        },
    )


class EventListingFilterTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        reset_site_root_paths()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)

        cls.webinar = EventType.objects.create(name="Webinar", slug="webinar")
        cls.meetup = EventType.objects.create(name="Meetup", slug="meetup")

        today = timezone.localdate()
        cls.upcoming_event = _event(
            title="Upcoming webinar",
            event_type=cls.webinar,
            start_date=today + datetime.timedelta(days=5),
        )
        cls.past_event = _event(
            title="Past meetup",
            event_type=cls.meetup,
            start_date=today - datetime.timedelta(days=5),
        )

        cls.event_index = EventIndexPage(
            title="Events", no_events_message="<p>No events</p>"
        )
        cls.homepage.add_child(instance=cls.event_index)
        cls.event_index.events = [cls.upcoming_event, cls.past_event]
        cls.event_index.save()

    def _titles(self, response):
        return [event.get("title") for event in response.context["events"]]

    def test_no_timing_selected_shows_upcoming_only_and_has_no_filters(self):
        response = self.client.get(self.event_index.url)

        self.assertEqual(self._titles(response), ["Upcoming webinar"])
        self.assertFalse(response.context["filter_state"].has_filters)

    def test_timing_upcoming_shows_upcoming_only(self):
        response = self.client.get(self.event_index.url, {"timing": "upcoming"})

        self.assertEqual(self._titles(response), ["Upcoming webinar"])
        self.assertTrue(response.context["filter_state"].has_filters)

    def test_timing_past_shows_past_only(self):
        response = self.client.get(self.event_index.url, {"timing": "past"})

        self.assertEqual(self._titles(response), ["Past meetup"])

    def test_both_timings_shows_all_events_upcoming_first(self):
        response = self.client.get(
            self.event_index.url, {"timing": ["upcoming", "past"]}
        )

        self.assertEqual(self._titles(response), ["Upcoming webinar", "Past meetup"])

    def test_timing_options_render_as_checkboxes_and_nothing_is_force_checked(self):
        response = self.client.get(self.event_index.url)
        content = response.content.decode()

        upcoming_input = _find_input(content, name="timing", value="upcoming")
        past_input = _find_input(content, name="timing", value="past")

        self.assertIn('type="checkbox"', upcoming_input)
        self.assertIn('type="checkbox"', past_input)
        self.assertNotIn("checked", upcoming_input)
        self.assertNotIn("checked", past_input)

    def test_selected_timing_checkbox_is_checked(self):
        response = self.client.get(self.event_index.url, {"timing": "past"})
        content = response.content.decode()

        upcoming_input = _find_input(content, name="timing", value="upcoming")
        past_input = _find_input(content, name="timing", value="past")

        self.assertNotIn("checked", upcoming_input)
        self.assertIn("checked", past_input)

    def test_legacy_filter_param_still_works_for_upcoming(self):
        response = self.client.get(self.event_index.url, {"filter": "upcoming"})

        self.assertEqual(self._titles(response), ["Upcoming webinar"])

    def test_legacy_filter_param_still_works_for_past(self):
        response = self.client.get(self.event_index.url, {"filter": "past"})

        self.assertEqual(self._titles(response), ["Past meetup"])

    def test_unknown_type_slug_alongside_valid_slug_is_ignored_not_fatal(self):
        response = self.client.get(
            self.event_index.url,
            {"timing": ["upcoming", "past"], "type": ["webinar", "does-not-exist"]},
        )

        self.assertEqual(self._titles(response), ["Upcoming webinar"])
        self.assertEqual(response.context["filter_state"].types, ("webinar",))


def _find_input(content: str, *, name: str, value: str) -> str:
    """Return the `<input ...>` tag for a given checkbox name/value pair."""
    pattern = re.compile(
        r"<input[^>]*name=\"%s\"[^>]*value=\"%s\"[^>]*>" % (name, value)
    )
    match = pattern.search(content)
    assert match, f"No input found for name={name!r} value={value!r}"
    return match.group(0)
