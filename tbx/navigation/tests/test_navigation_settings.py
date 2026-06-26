from unittest.mock import patch

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import SimpleTestCase

from wagtail.admin.panels.base import get_form_for_model
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.navigation.models import NavigationSettings
from tbx.navigation.utils import (
    PRIMARY_NAV_CACHE_TIMEOUT,
    PRIMARY_NAV_CACHE_VERSION,
    _primary_nav_cache_key,
    get_primary_nav_dropdowns,
)


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


class NavigationSettingsPrimaryNavCacheTestCase(WagtailPageTestCase):
    def test_save_rebuilds_primary_nav_cache(self):
        site = Site.objects.get(is_default_site=True)
        nav_settings = NavigationSettings.for_site(site)
        cache_key = _primary_nav_cache_key(site.pk)

        cache.delete(cache_key, version=PRIMARY_NAV_CACHE_VERSION)
        dropdowns = get_primary_nav_dropdowns(site)
        self.assertEqual(len(dropdowns), len(nav_settings.primary_navigation))
        self.assertIsNotNone(cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION))

        nav_settings.save()
        cached_after_save = cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION)
        self.assertIsNotNone(cached_after_save)
        self.assertEqual(len(cached_after_save), len(nav_settings.primary_navigation))

    def test_get_primary_nav_dropdowns_rebuilds_when_cache_missing(self):
        site = Site.objects.get(is_default_site=True)
        nav_settings = NavigationSettings.for_site(site)
        cache_key = _primary_nav_cache_key(site.pk)

        cache.delete(cache_key, version=PRIMARY_NAV_CACHE_VERSION)
        dropdowns = get_primary_nav_dropdowns(site)

        self.assertEqual(len(dropdowns), len(nav_settings.primary_navigation))
        self.assertIsNotNone(cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION))

    def test_page_publish_invalidates_primary_nav_cache(self):
        from tbx.core.factories import HomePageFactory

        site = Site.objects.get(is_default_site=True)
        cache_key = _primary_nav_cache_key(site.pk)
        page = HomePageFactory(parent=site.root_page, title="Newly published")

        # In production Page.get_site() resolves via Wagtail's site
        # root-paths cache; the test fixture doesn't line those up with
        # the factory's url_path, so patch get_site to return the real
        # site we care about.
        with patch.object(type(page), "get_site", return_value=site):
            cache.set(cache_key, ["stale"], 600, version=PRIMARY_NAV_CACHE_VERSION)
            page.save_revision().publish()
            self.assertIsNone(
                cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION)
            )

            cache.set(cache_key, ["stale"], 600, version=PRIMARY_NAV_CACHE_VERSION)
            page.unpublish()
            self.assertIsNone(
                cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION)
            )

    def test_page_publish_without_site_does_not_error(self):
        from tbx.core.factories import HomePageFactory

        site = Site.objects.get(is_default_site=True)
        page = HomePageFactory(parent=site.root_page, title="Orphan")

        # When Page.get_site() returns None (e.g. unrouteable page) the
        # signal handler should short-circuit without raising.
        with patch.object(type(page), "get_site", return_value=None):
            page.save_revision().publish()  # must not raise

    @patch("tbx.navigation.utils.cache.get_or_set")
    def test_get_primary_nav_dropdowns_passes_timeout_and_version(
        self, mock_get_or_set
    ):
        site = Site.objects.get(is_default_site=True)
        # Ensure NavigationSettings exists so for_site() doesn't trigger
        # a save() (and thus a rebuild) inside the call under test.
        nav_settings = NavigationSettings.for_site(site)
        mock_get_or_set.return_value = [None] * len(nav_settings.primary_navigation)
        mock_get_or_set.reset_mock()

        get_primary_nav_dropdowns(site)

        mock_get_or_set.assert_called_once()
        self.assertEqual(
            mock_get_or_set.call_args[0][2], PRIMARY_NAV_CACHE_TIMEOUT
        )
        self.assertEqual(
            mock_get_or_set.call_args.kwargs["version"], PRIMARY_NAV_CACHE_VERSION
        )
