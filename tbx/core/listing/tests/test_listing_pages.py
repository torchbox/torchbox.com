from django.core.paginator import Page as PaginatorPage

from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import HomePageFactory
from tbx.divisions.factories import DivisionPageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory


class BlogListingFilterTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
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
        self.assertContains(response, 'id="listing-filter-toggle-service"', count=1)
        self.assertContains(response, 'id="listing-filter-service"', count=1)
        self.assertContains(response, 'id="listing-filter-toggle-culture"', count=1)
        self.assertContains(response, 'id="listing-filter-culture"', count=1)

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

    def test_seo_title_for_single_filter(self):
        response = self.client.get(
            self.blog_index.url,
            {"service": "ai"},
        )
        self.assertContains(response, '<title id="document-title">News filtered by AI')
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
            headers={"hx-request": "true"}
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
            headers={"hx-request": "true"}
        )
        clear_url = response.context["clear_filters_url"]
        response = self.client.get(clear_url, headers={"hx-request": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_filters"], [])
        self.assertNotContains(response, "listing-filters__active-item")

    def test_htmx_request_returns_partial_template(self):
        response = self.client.get(
            self.blog_index.url,
            {"service": "ai"},
            headers={"hx-request": "true"}
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

    def test_legacy_filter_param_still_works(self):
        response = self.client.get(self.blog_index.url, {"filter": "ai"})
        self.assertEqual(response.status_code, 200)
        blog_posts = response.context["blog_posts"]
        self.assertEqual(list(blog_posts), [self.matching_post])


class WorkListingFilterTests(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        from tbx.work.factories import WorkIndexPageFactory, WorkPageFactory

        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)
        cls.division = DivisionPageFactory(parent=cls.homepage, title="Public")
        cls.work_index = WorkIndexPageFactory(parent=cls.division, title="Work")
        cls.service = ServiceFactory(name="Wagtail", slug="wagtail")
        cls.work_page = WorkPageFactory(
            parent=cls.work_index,
            title="Wagtail project",
            related_services=[cls.service],
        )
        WorkPageFactory(parent=cls.work_index, title="Other project")

    def test_get_context_returns_paginated_works(self):
        context = self.work_index.get_context(self._get_request())
        works = context["works"]
        self.assertIsInstance(works, PaginatorPage)
        titles = {work["title"] for work in works}
        self.assertIn(self.work_page.title, titles)

    def test_service_filter(self):
        response = self.client.get(self.work_index.url, {"service": "wagtail"})
        works = response.context["works"]
        self.assertEqual(len(works), 1)
        self.assertEqual(works[0]["title"], "Wagtail project")

    def _get_request(self):
        from wagtail.coreutils import get_dummy_request

        return get_dummy_request()
