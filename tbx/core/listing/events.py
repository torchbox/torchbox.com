from __future__ import annotations

from django.utils import timezone

from tbx.core.listing.filters import (
    EventFilterState,
    build_listing_urls_context,
    build_selected_filter_items,
    get_listing_paths,
    merge_selected_filter_options,
    paginate_queryset,
)
from tbx.core.models import EventType


TIMING_OPTIONS = (
    ("upcoming", "Upcoming events"),
    ("past", "Past events"),
)


def get_event_type_slugs() -> set[str]:
    return set(EventType.objects.values_list("slug", flat=True))


def get_event_filter_state(request) -> EventFilterState:
    return EventFilterState.from_request(
        request,
        valid_type_slugs=get_event_type_slugs(),
    )


def filter_events(events, filter_state: EventFilterState, *, today=None):
    today = today or timezone.localdate()
    timing = filter_state.timing or "upcoming"

    if timing == "past":
        filtered = [event for event in events if event.get("start_date") < today]
        filtered.sort(key=lambda event: event.get_start_date_time(), reverse=True)
    else:
        filtered = [event for event in events if today < event.get("start_date")]
        filtered.sort(key=lambda event: event.get_start_date_time())

    if filter_state.types:
        filtered = [
            event
            for event in filtered
            if any(
                getattr(event_type, "slug", None) in filter_state.types
                for event_type in event.get("type", [])
            )
        ]

    return filtered


def _filter_events_by_types(events, types: tuple[str, ...], *, today=None):
    today = today or timezone.localdate()
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
    filtered = _filter_events_by_types(events, filter_state.types, today=today)
    has_upcoming = any(today < event.get("start_date") for event in filtered)
    has_past = any(event.get("start_date") < today for event in filtered)

    available = []
    for value, label in TIMING_OPTIONS:
        if (value == "upcoming" and has_upcoming) or (value == "past" and has_past):
            available.append({"value": value, "label": label})

    if filter_state.timing:
        timing_labels = dict(TIMING_OPTIONS)
        available = merge_selected_filter_options(
            available,
            (filter_state.timing,),
            timing_labels,
        )

    return available


def get_available_event_types(events, filter_state: EventFilterState, *, today=None):
    today = today or timezone.localdate()
    timing_state = EventFilterState(timing=filter_state.timing, types=())
    filtered = filter_events(events, timing_state, today=today)

    available_slugs: set[str] = set()
    for event in filtered:
        for event_type in event.get("type", []):
            slug = getattr(event_type, "slug", None)
            if slug:
                available_slugs.add(slug)

    event_types = EventType.objects.order_by("name")
    type_labels = {event_type.slug: event_type.name for event_type in event_types}
    options = [
        {"value": event_type.slug, "label": event_type.name}
        for event_type in event_types
        if event_type.slug in available_slugs
    ]
    return merge_selected_filter_options(
        options,
        filter_state.types,
        type_labels,
    )


def _event_listing_filter_visibility(
    events,
    filter_state: EventFilterState,
    listing_filters: dict,
) -> dict[str, bool]:
    """Whether each events dropdown should be shown (baseline options or active selection)."""
    if filter_state.has_filters:
        listing_filters = {
            "timings": get_available_event_timings(events, EventFilterState()),
            "types": get_available_event_types(events, EventFilterState()),
        }

    return {
        "timing": bool(listing_filters["timings"]) or bool(filter_state.timing),
        "type": bool(listing_filters["types"]) or bool(filter_state.types),
    }


def build_events_listing_context(page, request, events):
    filter_state = get_event_filter_state(request)
    filtered_events = filter_events(events, filter_state)

    page_number = request.GET.get("page", 1)
    paginated_events = paginate_queryset(filtered_events, page_number, 10)

    event_types = EventType.objects.order_by("name")
    type_labels = {event_type.slug: event_type.name for event_type in event_types}
    timing_labels = dict(TIMING_OPTIONS)
    timing_options = get_available_event_timings(events, filter_state)
    type_options = get_available_event_types(events, filter_state)
    listing_filters = {
        "timings": timing_options,
        "types": type_options,
    }

    listing_path, absolute_base_url = get_listing_paths(page, request)
    current_absolute_url = absolute_base_url
    if query := filter_state.urlencode(page=page_number):
        current_absolute_url = f"{absolute_base_url}?{query}"

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
        ),
        **build_listing_urls_context(
            listing_path=listing_path,
            filter_state=filter_state,
            selected_filters=selected_filters,
            page_title=page.title,
            absolute_base_url=absolute_base_url,
            current_absolute_url=current_absolute_url,
            has_page_param="page" in request.GET,
        ),
        "listing_htmx_enabled": True,
        "listing_filters_template": "patterns/molecules/listing-filters/listing-filters--events.html",
        "listing_results_template": "patterns/pages/listing/listing_results--events.html",
    }
