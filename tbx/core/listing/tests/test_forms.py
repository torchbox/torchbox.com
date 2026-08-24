from django.test import SimpleTestCase

from tbx.core.listing.forms import EventFilterForm, TaxonomyFilterForm


class TaxonomyFilterFormTests(SimpleTestCase):
    choices = {
        "sector_choices": [("charity", "Charity"), ("health", "Health")],
        "service_choices": [("design", "Design"), ("strategy", "Strategy")],
    }

    def test_keeps_known_slugs(self):
        form = TaxonomyFilterForm(
            {"sector": ["charity", "health"], "service": ["design"]},
            **self.choices,
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["sector"], ["charity", "health"])
        self.assertEqual(form.cleaned_data["service"], ["design"])

    def test_drops_unknown_slugs(self):
        form = TaxonomyFilterForm(
            {"sector": ["charity", "bogus"], "service": ["nope"]},
            **self.choices,
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["sector"], ["charity"])
        self.assertEqual(form.cleaned_data["service"], [])

    def test_empty_query_is_valid(self):
        form = TaxonomyFilterForm({}, **self.choices)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["sector"], [])
        self.assertEqual(form.cleaned_data["service"], [])


class EventFilterFormTests(SimpleTestCase):
    def test_timing_and_type_kept(self):
        form = EventFilterForm(
            {"timing": ["past"], "type": ["webinar"]},
            type_choices=[("webinar", "Webinar")],
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["timing"], ["past"])
        self.assertEqual(form.cleaned_data["type"], ["webinar"])

    def test_unknown_timing_and_type_dropped(self):
        form = EventFilterForm(
            {"timing": ["sometime"], "type": ["bogus"]},
            type_choices=[("webinar", "Webinar")],
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["timing"], [])
        self.assertEqual(form.cleaned_data["type"], [])
