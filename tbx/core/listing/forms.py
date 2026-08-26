from django import forms


# Timing choices for the events "When" filter. An empty selection displays
# upcoming events only by default.
TIMING_CHOICES = (
    ("upcoming", "Upcoming"),
    ("past", "Past"),
)


class LenientMultipleChoiceField(forms.MultipleChoiceField):
    """A multiple-choice field that silently drops unknown values.

    Filter choices come from the taxonomy terms currently in use, so a stale or
    renamed slug in a bookmarked URL should be ignored rather than invalidate
    the whole field. We keep only submitted values that are still valid choices.
    """

    def clean(self, value):
        values = self.to_python(value)
        valid_values = {str(choice_value) for choice_value, _ in self.choices}
        return [value for value in values if value in valid_values]


class TaxonomyFilterForm(forms.Form):
    """Validates the Work and News listing filters (``?sector=`` / ``?service=``)."""

    sector = LenientMultipleChoiceField(required=False)
    service = LenientMultipleChoiceField(required=False)

    def __init__(self, *args, sector_choices=(), service_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sector"].choices = sector_choices
        self.fields["service"].choices = service_choices


class EventFilterForm(forms.Form):
    """Validates the Events listing filters (``?timing=`` / ``?type=``)."""

    timing = LenientMultipleChoiceField(required=False, choices=TIMING_CHOICES)
    type = LenientMultipleChoiceField(required=False)

    def __init__(self, *args, type_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].choices = type_choices
