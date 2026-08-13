from __future__ import annotations

from django.utils import timezone

from tbx.core.listing.filters import (
    DROPDOWN_LABELS,
    EventFilterState,
    build_listing_urls_context,
    build_selected_filter_items,
    dropdown_is_visible,
    merge_selected_filter_options,
    paginate_queryset,
)
from tbx.core.listing.forms import (
    TIMING_OPTIONS,
    EventFilterForm,
    build_event_filter_state,
)
from tbx.core.models import EventType


def get_event_type_choices() -> list[tuple[str, str]]:
    return [
        (event_type.slug, event_type.name)
        for event_type in EventType.objects.order_by("name")
    ]


ALL_TIMINGS = tuple(value for value, _ in TIMING_OPTIONS)


def get_event_filter_state(request, *, type_choices=None) -> EventFilterState:
    if type_choices is None:
        type_choices = get_event_type_choices()
    form = EventFilterForm(request.GET, type_choices=type_choices)
    return build_event_filter_state(form)


def filter_events(events, filter_state: EventFilterState, *, today=None):
    """Filter and order the events list for the selected timings and types.

    With no timing selected the listing shows its default view of upcoming events.
    Selecting both timings shows everything, upcoming first.
    """
    today = today or timezone.localdate()
    timings = filter_state.timings or ("upcoming",)

    filtered = []
    if "upcoming" in timings:
        filtered += sorted(
            (event for event in events if today < event.get("start_date")),
            key=lambda event: event.get_start_date_time(),
        )
    if "past" in timings:
        filtered += sorted(
            (event for event in events if event.get("start_date") < today),
            key=lambda event: event.get_start_date_time(),
            reverse=True,
        )

    return _filter_events_by_types(filtered, filter_state.types)


def _filter_events_by_types(events, types: tuple[str, ...]):
    if not types:
        return events

    return [
        event
        for event in events
        if any(
            getattr(event_type, "slug", None) in types
            for event_type in event.get("type", [])
        )
    ]


def get_available_event_timings(events, filter_state: EventFilterState, *, today=None):
    today = today or timezone.localdate()
    filtered = _filter_events_by_types(events, filter_state.types)
    has_upcoming = any(today < event.get("start_date") for event in filtered)
    has_past = any(event.get("start_date") < today for event in filtered)

    available = []
    for value, label in TIMING_OPTIONS:
        if (value == "upcoming" and has_upcoming) or (value == "past" and has_past):
            available.append({"value": value, "label": label})

    if filter_state.timings:
        available = merge_selected_filter_options(
            available,
            filter_state.timings,
            dict(TIMING_OPTIONS),
        )

    return available


def get_available_event_types(
    events,
    filter_state: EventFilterState,
    *,
    type_choices=None,
    today=None,
):
    today = today or timezone.localdate()
    timing_state = EventFilterState(timings=filter_state.timings, types=())
    filtered = filter_events(events, timing_state, today=today)

    available_slugs: set[str] = set()
    for event in filtered:
        for event_type in event.get("type", []):
            slug = getattr(event_type, "slug", None)
            if slug:
                available_slugs.add(slug)

    if type_choices is None:
        type_choices = get_event_type_choices()
    type_labels = dict(type_choices)
    options = [
        {"value": slug, "label": label}
        for slug, label in type_choices
        if slug in available_slugs
    ]
    return merge_selected_filter_options(options, filter_state.types, type_labels)


def build_events_listing_context(page, request, events):
    # Fetched once and threaded through: the choices validate the request, label the
    # pills and build the dropdown options, and they must all agree with each other.
    type_choices = get_event_type_choices()

    filter_state = get_event_filter_state(request, type_choices=type_choices)
    filtered_events = filter_events(events, filter_state)

    page_number = request.GET.get("page", 1)
    paginated_events = paginate_queryset(filtered_events, page_number, 10)

    timing_labels = dict(TIMING_OPTIONS)
    type_labels = dict(type_choices)
    listing_filters = {
        "timings": get_available_event_timings(events, filter_state),
        "types": get_available_event_types(
            events, filter_state, type_choices=type_choices
        ),
    }

    listing_path = page.get_url(request)
    selected_filters = build_selected_filter_items(
        listing_path,
        filter_state,
        filter_state.selected_labels(
            type_labels=type_labels,
            timing_labels=timing_labels,
        ),
    )

    return {
        "events": paginated_events,
        "filter_state": filter_state,
        "listing_filters": listing_filters,
        "listing_filter_visibility": _event_listing_filter_visibility(
            events,
            filter_state,
            listing_filters,
            type_choices=type_choices,
        ),
        "listing_result_count": paginated_events.paginator.count,
        **build_listing_urls_context(
            listing_path=listing_path,
            filter_state=filter_state,
            selected_filters=selected_filters,
            page_title=page.title,
        ),
        "listing_htmx_enabled": True,
        "listing_filters_template": "patterns/molecules/listing-filters/listing-filters--events.html",
        "listing_results_template": "patterns/pages/listing/listing_results--events.html",
    }


def _event_listing_filter_visibility(
    events,
    filter_state: EventFilterState,
    listing_filters: dict,
    *,
    type_choices=None,
) -> dict[str, bool]:
    """Whether each events dropdown should be shown.

    As with the taxonomy listings, visibility is judged on the unfiltered listing so
    dropdowns don't disappear once a filter narrows the options.
    """
    baseline_filters = listing_filters
    if filter_state.has_filters:
        baseline_filters = {
            "timings": get_available_event_timings(events, EventFilterState()),
            # Every timing, explicitly. An empty `timings` would fall through to
            # `filter_events`' default upcoming-only view, which would hide the whole
            # dropdown for a type only ever used by past events.
            "types": get_available_event_types(
                events,
                EventFilterState(timings=ALL_TIMINGS),
                type_choices=type_choices,
            ),
        }

    return {
        "timing": dropdown_is_visible(
            baseline_filters["timings"], filter_state.timings, DROPDOWN_LABELS["timing"]
        ),
        "type": dropdown_is_visible(
            baseline_filters["types"], filter_state.types, DROPDOWN_LABELS["type"]
        ),
    }
