from __future__ import annotations

from django import forms
from django.http import QueryDict

from tbx.core.listing.filters import LEGACY_FILTER_PARAM, EventFilterState


TIMING_OPTIONS = (
    ("upcoming", "Upcoming events"),
    ("past", "Past events"),
)

LEGACY_TIMING_SLUGS = frozenset(value for value, _ in TIMING_OPTIONS)


class LenientMultipleChoiceField(forms.MultipleChoiceField):
    """A multiple choice field that drops unrecognised values.

    Filters are driven by URLs that outlive the content they point at, so a stale or
    hand-edited value shouldn't invalidate the whole dimension and silently widen the
    result set. Values are still checked against the field's choices — unknown ones
    are just discarded rather than raising.
    """

    def clean(self, value):
        allowed = {str(key) for key, _ in self.choices}
        values = [value for value in self.to_python(value) if value in allowed]
        if self.required and not values:
            raise forms.ValidationError(
                self.error_messages["required"], code="required"
            )
        return values


class EventFilterForm(forms.Form):
    """Validates the `?timing=` / `?type=` params on the events listing.

    The events listing filters a Python list of StreamField values rather than a
    queryset, so a plain form validates the query parameters. `cleaned_data` is
    turned into an `EventFilterState` by `build_event_filter_state`.
    """

    timing = LenientMultipleChoiceField(choices=TIMING_OPTIONS, required=False)
    type = LenientMultipleChoiceField(choices=(), required=False)

    def __init__(self, data=None, *, type_choices=()):
        super().__init__(data=_resolve_legacy_timing_param(data))
        self.fields["type"].choices = list(type_choices)


def _resolve_legacy_timing_param(data) -> QueryDict | None:
    """Map the legacy `?filter=upcoming|past` param onto `?timing=`."""
    if data is None:
        return None
    if data.getlist("timing"):
        return data
    legacy_slug = data.get(LEGACY_FILTER_PARAM)
    if legacy_slug not in LEGACY_TIMING_SLUGS:
        return data
    data = data.copy()
    data.setlist("timing", [legacy_slug])
    return data


def build_event_filter_state(form: EventFilterForm) -> EventFilterState:
    """Turn validated form data into the presentation-layer filter state."""
    form.is_valid()
    cleaned_data = getattr(form, "cleaned_data", {})
    return EventFilterState(
        timings=_in_choice_order(form.fields["timing"], cleaned_data.get("timing")),
        types=_in_choice_order(form.fields["type"], cleaned_data.get("type")),
    )


def _in_choice_order(field, selected) -> tuple[str, ...]:
    """Order selections by the field's choices so pills and URLs stay stable."""
    selected = set(selected or ())
    return tuple(str(key) for key, _ in field.choices if str(key) in selected)
