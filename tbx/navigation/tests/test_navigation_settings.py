from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import SimpleTestCase

from wagtail.admin.panels.base import get_form_for_model
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.navigation.models import NavigationSettings


class NavigationSettingsFormTestCase(SimpleTestCase):
    def setUp(self):
        self.form_class = get_form_for_model(
            NavigationSettings,
            fields=[
                "footer_newsletter_cta_url",
                "footer_newsletter_cta_text",
            ],
        )

    def test_cta_optional(self):
        form = self.form_class(
            data={"footer_newsletter_cta_url": "", "footer_newsletter_cta_text": ""}
        )
        self.assertTrue(form.is_valid())

    def test_cta_text_required_if_url_supplied(self):
        form = self.form_class(
            data={
                "footer_newsletter_cta_url": "https://example.com",
                "footer_newsletter_cta_text": "",
            }
        )
        self.assertFormError(
            form,
            "footer_newsletter_cta_text",
            "The CTA footer text is required when a URL is supplied",
        )


class NavigationSettingsCacheTestCase(WagtailPageTestCase):
    def test_save_clears_nav_fragment_cache(self):
        site = Site.objects.get(is_default_site=True)
        nav_settings = NavigationSettings.for_site(site)
        fragment_keys = [
            "primarynav",
            "primarynavmobile",
            "footerlinks",
            "headeractions",
        ]

        for fragment_name in fragment_keys:
            for is_pattern_library in [True, "", False]:
                key = make_template_fragment_key(
                    fragment_name, vary_on=(site.pk, is_pattern_library)
                )
                cache.set(key, "cached fragment", 600)

        nav_settings.save()

        for fragment_name in fragment_keys:
            for is_pattern_library in [True, "", False]:
                key = make_template_fragment_key(
                    fragment_name, vary_on=(site.pk, is_pattern_library)
                )
                self.assertIsNone(cache.get(key))
