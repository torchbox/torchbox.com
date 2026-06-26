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
    get_primary_navigation,
)

# A sentinel non-empty payload — get_primary_navigation only writes to the
# cache when the rebuild returns something, so tests that assert cache
# population must patch _build_primary_navigation to a non-empty list.
_SENTINEL_NAV = [{"text": "Home", "url": "/", "page_id": None,
                  "style": "none", "main_heading": "", "supporting_heading": "",
                  "main_items": [], "supporting_items": []}]


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
    @patch("tbx.navigation.utils._build_primary_navigation")
    def test_save_rebuilds_primary_nav_cache(self, mock_build):
        mock_build.return_value = list(_SENTINEL_NAV)
        site = Site.objects.get(is_default_site=True)
        nav_settings = NavigationSettings.for_site(site)
        cache_key = _primary_nav_cache_key(site.pk)

        cache.delete(cache_key, version=PRIMARY_NAV_CACHE_VERSION)
        dropdowns = get_primary_navigation(site)
        self.assertEqual(dropdowns, _SENTINEL_NAV)
        self.assertEqual(
            cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION), _SENTINEL_NAV
        )

        nav_settings.save()
        self.assertEqual(
            cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION), _SENTINEL_NAV
        )

    @patch("tbx.navigation.utils._build_primary_navigation")
    def test_get_primary_navigation_rebuilds_when_cache_missing(self, mock_build):
        mock_build.return_value = list(_SENTINEL_NAV)
        site = Site.objects.get(is_default_site=True)
        cache_key = _primary_nav_cache_key(site.pk)

        cache.delete(cache_key, version=PRIMARY_NAV_CACHE_VERSION)
        dropdowns = get_primary_navigation(site)

        self.assertEqual(dropdowns, _SENTINEL_NAV)
        self.assertEqual(
            cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION), _SENTINEL_NAV
        )

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

    @patch("tbx.navigation.utils._build_primary_navigation")
    @patch("tbx.navigation.utils.cache.set")
    def test_get_primary_navigation_writes_with_timeout_and_version(
        self, mock_set, mock_build
    ):
        mock_build.return_value = list(_SENTINEL_NAV)
        site = Site.objects.get(is_default_site=True)
        cache.delete(
            _primary_nav_cache_key(site.pk), version=PRIMARY_NAV_CACHE_VERSION
        )

        get_primary_navigation(site)

        mock_set.assert_called_once()
        self.assertEqual(mock_set.call_args[0][2], PRIMARY_NAV_CACHE_TIMEOUT)
        self.assertEqual(
            mock_set.call_args.kwargs["version"], PRIMARY_NAV_CACHE_VERSION
        )

    @patch("tbx.navigation.utils._build_primary_navigation")
    def test_empty_cached_value_triggers_rebuild(self, mock_build):
        mock_build.return_value = list(_SENTINEL_NAV)
        site = Site.objects.get(is_default_site=True)
        key = _primary_nav_cache_key(site.pk)
        # Poison the cache with an empty list — could happen if nav was
        # cached before any blocks were configured. The reader must rebuild.
        cache.set(key, [], 600, version=PRIMARY_NAV_CACHE_VERSION)

        resolved = get_primary_navigation(site)
        self.assertEqual(resolved, _SENTINEL_NAV)

    def test_page_publish_only_invalidates_own_site(self):
        from tbx.core.factories import HomePageFactory

        site_a = Site.objects.get(is_default_site=True)
        other_root = HomePageFactory(parent=site_a.root_page, title="Site B root")
        site_b = Site.objects.create(
            hostname="site-b.test", port=80, root_page=other_root
        )
        key_a = _primary_nav_cache_key(site_a.pk)
        key_b = _primary_nav_cache_key(site_b.pk)

        page = HomePageFactory(parent=site_a.root_page, title="On site A")
        with patch.object(type(page), "get_site", return_value=site_a):
            cache.set(key_a, ["stale-a"], 600, version=PRIMARY_NAV_CACHE_VERSION)
            cache.set(key_b, ["stale-b"], 600, version=PRIMARY_NAV_CACHE_VERSION)
            page.save_revision().publish()

            self.assertIsNone(
                cache.get(key_a, version=PRIMARY_NAV_CACHE_VERSION)
            )
            self.assertEqual(
                cache.get(key_b, version=PRIMARY_NAV_CACHE_VERSION), ["stale-b"]
            )

    def test_page_move_invalidates_primary_nav_cache(self):
        from tbx.core.factories import HomePageFactory

        site = Site.objects.get(is_default_site=True)
        cache_key = _primary_nav_cache_key(site.pk)
        page = HomePageFactory(parent=site.root_page, title="Moves")
        new_parent = HomePageFactory(parent=site.root_page, title="New parent")

        with patch.object(type(page), "get_site", return_value=site):
            cache.set(cache_key, ["stale"], 600, version=PRIMARY_NAV_CACHE_VERSION)
            page.move(new_parent, pos="last-child")
            self.assertIsNone(
                cache.get(cache_key, version=PRIMARY_NAV_CACHE_VERSION)
            )
