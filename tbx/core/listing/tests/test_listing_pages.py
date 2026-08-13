from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import HomePageFactory
from tbx.core.listing.tests import dropdown_tag as _dropdown_tag
from tbx.core.listing.tests import reset_site_root_paths as _reset_site_root_paths
from tbx.divisions.factories import DivisionPageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.work.factories import WorkIndexPageFactory, WorkPageFactory


class BlogListingFilterTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        _reset_site_root_paths()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)
        cls.blog_index = BlogIndexPageFactory(parent=cls.homepage, title="News")
        cls.sector = SectorFactory(name="Public sector", slug="public-sector")
        cls.service = ServiceFactory(name="AI", slug="ai")
        cls.matching_post = BlogPageFactory(
            parent=cls.blog_index,
            title="Matching post",
            related_sectors=[cls.sector],
            related_services=[cls.service],
        )
        cls.sector_post = BlogPageFactory(
            parent=cls.blog_index,
            title="Sector post",
            related_sectors=[cls.sector],
        )
        BlogPageFactory(parent=cls.blog_index, title="Other post")

    def test_culture_services_split_in_listing_filters(self):
        culture_service = ServiceFactory(name="Culture", slug="culture")
        BlogPageFactory(
            parent=self.blog_index,
            title="Culture post",
            related_services=[culture_service],
        )
        BlogPageFactory(
            parent=self.blog_index,
            title="AI post",
            related_services=[self.service],
        )

        response = self.client.get(self.blog_index.url)
        listing_filters = response.context["listing_filters"]

        self.assertEqual(
            listing_filters["services"],
            [{"value": "ai", "label": "AI"}],
        )
        self.assertEqual(
            listing_filters["culture"],
            [{"value": "culture", "label": "Culture"}],
        )
        self.assertEqual(response.context["selected_services"], ())
        self.assertEqual(response.context["selected_culture"], ())
        self.assertNotIn("divisions", listing_filters)
        self.assertContains(response, 'id="listing-filter-dropdown-service"', count=1)
        self.assertContains(response, 'id="listing-filter-service-options"', count=1)
        self.assertContains(response, 'id="listing-filter-dropdown-culture"', count=1)
        self.assertContains(response, 'id="listing-filter-culture-options"', count=1)

    def test_valid_but_unused_sector_filter_does_not_error(self):
        SectorFactory(name="Unused sector", slug="unused-sector")
        response = self.client.get(
            self.blog_index.url,
            {"sector": "unused-sector"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["blog_posts"]), [])
        self.assertEqual(
            response.context["selected_filters"][0]["label"],
            "Unused sector",
        )
        self.assertContains(response, "No results match your filters")
        self.assertContains(response, 'id="listing-filter-dropdown-sector"', count=1)

    def test_unknown_slug_alongside_valid_slug_is_ignored_not_fatal(self):
        response = self.client.get(
            self.blog_index.url,
            {"sector": ["public-sector", "does-not-exist"]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {post.title for post in response.context["blog_posts"]},
            {"Sector post", "Matching post"},
        )
        self.assertEqual(response.context["filter_state"].sectors, ("public-sector",))

    def test_dropdown_stays_visible_when_facet_narrowing_empties_options(self):
        other_sector = SectorFactory(name="Arts", slug="arts")
        wagtail = ServiceFactory(name="Wagtail", slug="wagtail")
        BlogPageFactory(
            parent=self.blog_index,
            title="Arts wagtail post",
            related_sectors=[other_sector],
            related_services=[wagtail],
        )

        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector", "service": "wagtail"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["blog_posts"]), [])
        self.assertContains(response, "No results match your filters")
        self.assertContains(response, 'id="listing-filter-dropdown-service"', count=1)
        self.assertContains(response, 'id="listing-filter-dropdown-sector"', count=1)

    def test_valid_but_unused_service_filter_does_not_error(self):
        ServiceFactory(name="Unused service", slug="unused-service")
        response = self.client.get(
            self.blog_index.url,
            {"service": "unused-service"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["blog_posts"]), [])
        self.assertEqual(
            response.context["selected_filters"][0]["label"],
            "Unused service",
        )

    def test_single_filter_limits_results(self):
        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector"},
        )
        self.assertEqual(response.status_code, 200)
        blog_posts = response.context["blog_posts"]
        self.assertEqual(
            {post.title for post in blog_posts},
            {"Sector post", "Matching post"},
        )

    def test_multiple_filters_use_and_logic(self):
        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector", "service": "ai"},
        )
        self.assertEqual(response.status_code, 200)
        blog_posts = response.context["blog_posts"]
        self.assertEqual(list(blog_posts), [self.matching_post])

    def test_service_options_narrow_when_sector_selected(self):
        other_sector = SectorFactory(name="Arts", slug="arts")
        wagtail = ServiceFactory(name="Wagtail", slug="wagtail")
        BlogPageFactory(
            parent=self.blog_index,
            title="Arts wagtail post",
            related_sectors=[other_sector],
            related_services=[wagtail],
        )

        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["listing_filters"]["services"],
            [{"value": "ai", "label": "AI"}],
        )
        self.assertNotIn(
            "wagtail",
            {
                option["value"]
                for option in response.context["listing_filters"]["services"]
            },
        )

    def test_htmx_response_does_not_replace_filter_options(self):
        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector"},
            headers={"hx-request": "true"},
        )
        content = response.content.decode()
        self.assertNotIn('hx-swap-oob="innerHTML"', content)
        self.assertNotIn('id="listing-filter-service-options"', content)

    def test_seo_title_for_single_filter(self):
        response = self.client.get(
            self.blog_index.url,
            {"service": "ai"},
        )
        self.assertContains(response, '<title id="document-title">News filtered by AI')
        self.assertIsNone(response.context["listing_robots_content"])

    def test_no_filters_uses_plain_title_and_no_robots(self):
        response = self.client.get(self.blog_index.url)
        self.assertContains(response, '<title id="document-title">News')
        self.assertIsNone(response.context["listing_robots_content"])

    def test_multi_filter_is_noindex(self):
        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector", "service": "ai"},
        )
        self.assertEqual(
            response.context["listing_robots_content"], "noindex, nofollow"
        )
        self.assertContains(response, 'content="noindex, nofollow"')

    def test_htmx_partial_response_only_swaps_title_not_robots(self):
        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector", "service": "ai"},
            headers={"hx-request": "true"},
        )
        content = response.content.decode()
        self.assertIn('<title id="document-title" hx-swap-oob="true">', content)
        self.assertNotIn("noindex", content)
        self.assertNotIn('name="robots"', content)
        self.assertNotIn("canonical", content)

    def test_pagination_preserves_filters(self):
        for index in range(11):
            BlogPageFactory(
                parent=self.blog_index,
                title=f"Sector post {index}",
                related_sectors=[self.sector],
            )

        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector", "page": "2"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sector=public-sector")
        self.assertIsNone(response.context.get("listing_robots_content"))

    def test_htmx_remove_single_filter_preserves_others(self):
        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector", "service": "ai"},
            headers={"hx-request": "true"},
        )
        self.assertEqual(len(response.context["selected_filters"]), 2)

        remove_url = response.context["selected_filters"][0]["remove_url"]
        response = self.client.get(remove_url, headers={"hx-request": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["selected_filters"]), 1)
        self.assertEqual(response.context["selected_filters"][0]["param"], "service")
        self.assertEqual(
            response.content.decode().count("listing-filters__active-item"), 2
        )

    def test_htmx_clear_filters_removes_active_pills(self):
        response = self.client.get(
            self.blog_index.url,
            {"sector": "public-sector", "service": "ai"},
            headers={"hx-request": "true"},
        )
        clear_url = response.context["clear_filters_url"]
        response = self.client.get(clear_url, headers={"hx-request": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_filters"], [])
        self.assertNotContains(response, "listing-filters__active-item")

    def test_htmx_request_returns_partial_template(self):
        response = self.client.get(
            self.blog_index.url, {"service": "ai"}, headers={"hx-request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "patterns/pages/listing/listing_panel_partial.html",
        )
        self.assertContains(response, "data-listing-filters")
        self.assertContains(response, "listing-panel__results")
        self.assertEqual(response.context["listing_base_url"], self.blog_index.url)

    def test_non_js_form_submission_filters_results(self):
        response = self.client.get(
            self.blog_index.url,
            {"service": "ai"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'method="get"')
        self.assertContains(response, f'action="{self.blog_index.url}"')
        self.assertContains(response, "Apply filters")
        self.assertContains(response, "data-listing-filters-submit")
        self.assertEqual(list(response.context["blog_posts"]), [self.matching_post])

    def test_legacy_filter_param_still_works_for_service(self):
        response = self.client.get(self.blog_index.url, {"filter": "ai"})
        self.assertEqual(response.status_code, 200)
        blog_posts = response.context["blog_posts"]
        self.assertEqual(list(blog_posts), [self.matching_post])

    def test_legacy_filter_param_still_works_for_sector(self):
        response = self.client.get(self.blog_index.url, {"filter": "public-sector"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {post.title for post in response.context["blog_posts"]},
            {"Sector post", "Matching post"},
        )

    def test_legacy_filter_param_still_works_for_division(self):
        division = DivisionPageFactory(parent=self.homepage, title="Public")
        division_post = BlogPageFactory(
            parent=self.blog_index,
            title="Division post",
            division=division,
        )

        response = self.client.get(self.blog_index.url, {"filter": division.slug})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["blog_posts"]), [division_post])

    def test_division_filter_works_on_blog_listing(self):
        division = DivisionPageFactory(parent=self.homepage, title="Public")
        division_post = BlogPageFactory(
            parent=self.blog_index,
            title="Division post",
            division=division,
        )

        response = self.client.get(self.blog_index.url, {"division": division.slug})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["blog_posts"]), [division_post])


class DropdownVisibilityTests(WagtailPageTestCase):
    """The single-duplicate-option visibility rule (`dropdown_is_visible`).

    A dropdown whose unfiltered listing offers exactly one option, and that
    option's label repeats the dropdown's own label, tells the user nothing
    they can act on and is hidden.
    """

    @classmethod
    def setUpTestData(cls):
        _reset_site_root_paths()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)
        cls.blog_index = BlogIndexPageFactory(parent=cls.homepage, title="News")

    def test_single_culture_option_matching_dropdown_label_is_hidden(self):
        culture_service = ServiceFactory(name="Culture", slug="culture")
        BlogPageFactory(
            parent=self.blog_index,
            title="Culture post",
            related_services=[culture_service],
        )

        response = self.client.get(self.blog_index.url)

        self.assertFalse(response.context["listing_filter_visibility"]["culture"])
        self.assertContains(response, 'id="listing-filter-dropdown-culture"', count=1)
        self.assertIn("hidden", _dropdown_tag(response.content.decode(), "culture"))

    def test_two_culture_options_stays_visible(self):
        culture_service = ServiceFactory(name="Culture", slug="culture")
        sustainability = ServiceFactory(name="Sustainability", slug="sustainability")
        BlogPageFactory(
            parent=self.blog_index,
            title="Culture post",
            related_services=[culture_service],
        )
        BlogPageFactory(
            parent=self.blog_index,
            title="Sustainability post",
            related_services=[sustainability],
        )

        response = self.client.get(self.blog_index.url)

        self.assertTrue(response.context["listing_filter_visibility"]["culture"])

    def test_single_sector_option_with_different_label_stays_visible(self):
        sector = SectorFactory(name="Public sector", slug="public-sector")
        BlogPageFactory(
            parent=self.blog_index,
            title="Sector post",
            related_sectors=[sector],
        )

        response = self.client.get(self.blog_index.url)

        self.assertTrue(response.context["listing_filter_visibility"]["sector"])

    def test_active_culture_selection_keeps_dropdown_visible(self):
        culture_service = ServiceFactory(name="Culture", slug="culture")
        BlogPageFactory(
            parent=self.blog_index,
            title="Culture post",
            related_services=[culture_service],
        )

        response = self.client.get(self.blog_index.url, {"service": "culture"})

        self.assertTrue(response.context["listing_filter_visibility"]["culture"])
        self.assertNotIn("hidden", _dropdown_tag(response.content.decode(), "culture"))


class WorkListingFilterTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        _reset_site_root_paths()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)
        cls.top_division = DivisionPageFactory(parent=cls.homepage, title="Public")
        cls.work_index = WorkIndexPageFactory(parent=cls.top_division, title="Work")
        cls.service = ServiceFactory(name="Wagtail", slug="wagtail")
        cls.work_page = WorkPageFactory(
            parent=cls.work_index,
            title="Wagtail project",
            related_services=[cls.service],
        )
        WorkPageFactory(parent=cls.work_index, title="Other project")

    def test_get_context_returns_paginated_works(self):
        from django.core.paginator import Page as PaginatorPage
        from wagtail.coreutils import get_dummy_request

        context = self.work_index.get_context(get_dummy_request())
        works = context["works"]
        self.assertIsInstance(works, PaginatorPage)
        titles = {work.title for work in works}
        self.assertIn(self.work_page.title, titles)

    def test_service_filter(self):
        response = self.client.get(self.work_index.url, {"service": "wagtail"})
        works = response.context["works"]
        self.assertEqual(len(works), 1)
        self.assertEqual(works[0].title, "Wagtail project")

    def test_unknown_slug_alongside_valid_slug_is_ignored_not_fatal(self):
        response = self.client.get(
            self.work_index.url,
            {"service": ["wagtail", "does-not-exist"]},
        )
        self.assertEqual(response.status_code, 200)
        works = response.context["works"]
        self.assertEqual(len(works), 1)
        self.assertEqual(works[0].title, "Wagtail project")

    def test_division_filter_works_on_work_listing(self):
        """`?division=` used to 500 on the work listing: the old filter ran
        `Q(division__slug__in=...)` against a base `Page` queryset, which has no
        `division` field of its own (only the concrete `WorkPage`/
        `HistoricalWorkPage` models do). This covers both listing types so the
        regression can't come back unnoticed.
        """
        other_division = DivisionPageFactory(parent=self.homepage, title="Private")
        division_work = WorkPageFactory(
            parent=self.work_index,
            title="Division project",
            division=other_division,
        )

        response = self.client.get(
            self.work_index.url, {"division": other_division.slug}
        )

        self.assertEqual(response.status_code, 200)
        works = response.context["works"]
        self.assertEqual([work.title for work in works], [division_work.title])
