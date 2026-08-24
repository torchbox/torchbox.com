from django.core.paginator import Paginator
from django.utils import timezone

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField

from tbx.core.listing.context import build_listing_filter_context
from tbx.core.listing.forms import EventFilterForm
from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField
from tbx.events.blocks import EventItemBlock


class EventIndexPage(BasePage):
    template = "patterns/pages/events/events_listing.html"
    no_events_message = RichTextField(
        features=["bold", "italic", "link", "superscript", "subscript"],
        help_text="Message to display if there are no events",
    )

    parent_page_types = ["torchbox.HomePage"]
    subpage_types = []

    events = StreamField([("event", EventItemBlock())], blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("no_events_message"),
        FieldPanel("events"),
    ]

    def get_event_type_choices(self):
        """Event-type (slug, name) choices for the types actually in use."""
        types = {}
        for event in self.events:
            for event_type in event.value.get("type"):
                types[event_type.slug] = event_type.name
        return sorted(types.items(), key=lambda item: item[1].lower())

    def get_events(self, timings=None, types=None):
        """Filter and order the listing's events.

        ``timings`` is a list drawn from ``upcoming``/``past``; an empty list
        defaults to upcoming only. ``types`` is a list of event-type slugs
        (OR-matched: an event is kept if it has any of the selected types).
        """
        today = timezone.localdate()
        timings = timings or ["upcoming"]

        def matches_type(value):
            if not types:
                return True
            return any(event_type.slug in types for event_type in value.get("type"))

        want_upcoming = "upcoming" in timings
        want_past = "past" in timings

        # Single pass over the StreamField, partitioning by timing.
        upcoming = []
        past = []
        for event in self.events:
            value = event.value
            if not matches_type(value):
                continue
            start_date = value.get("start_date")
            if want_upcoming and today < start_date:
                upcoming.append(value)
            elif want_past and start_date < today:
                past.append(value)

        events = []
        if want_upcoming:
            upcoming.sort(key=lambda value: value.get_start_date_time())
            events.extend(upcoming)
        if want_past:
            past.sort(key=lambda value: value.get_start_date_time(), reverse=True)
            events.extend(past)
        return events

    def get_context(self, request):
        context = super().get_context(request)

        # Validate the query string through a form; only trust cleaned_data.
        form = EventFilterForm(
            request.GET, type_choices=self.get_event_type_choices()
        )
        form.is_valid()

        events = self.get_events(
            timings=form.cleaned_data.get("timing"),
            types=form.cleaned_data.get("type"),
        )

        # Use `page` to filter.
        page = request.GET.get("page", 1)

        # Pagination
        paginator = Paginator(events, 10)  # Show 10 events per page
        paged_events = paginator.get_page(page)

        context.update(events=paged_events)
        context.update(
            build_listing_filter_context(
                request,
                form,
                dropdowns=(("timing", "When"), ("type", "Event type")),
            )
        )
        return context
