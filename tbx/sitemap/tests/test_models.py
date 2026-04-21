from wagtail.models import PageViewRestriction, Site
from wagtail.test.utils import WagtailPageTestCase

from tbx.core.factories import HomePageFactory, StandardPageFactory
from tbx.sitemap.factories import SitemapPageFactory
from tbx.sitemap.models import SitemapPage


class TestSitemapPageSections(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.home = HomePageFactory(parent=root)
        site.root_page = cls.home
        site.save()

        # A top-level section under home
        cls.section = StandardPageFactory(title="Work", parent=cls.home)
        # A live, public child page
        cls.live_page = StandardPageFactory(title="Our Work", parent=cls.section)
        # A draft (unpublished) child page
        cls.draft_page = StandardPageFactory(
            title="Draft Work", parent=cls.section, live=False
        )
        # A private child page (password-protected)
        cls.private_page = StandardPageFactory(title="Private Work", parent=cls.section)
        PageViewRestriction.objects.create(
            page=cls.private_page,
            restriction_type="password",
            password="secret123",  # noqa: S106
        )
        cls.sitemap_page = SitemapPageFactory(title="Sitemap", parent=cls.home)

    def _get_sections(self):
        # Re-fetch to bust the request-scoped cached_property
        page = SitemapPage.objects.get(pk=self.sitemap_page.pk)
        return page.sections

    def _top_level_pks(self, section):
        """Return PKs of the direct children of a section (root nodes of the tree)."""
        return [node["page"].pk for node in section["pages"]]

    def test_sections_excludes_draft_pages(self):
        sections = self._get_sections()
        work_section = next(s for s in sections if s["section"].pk == self.section.pk)
        page_pks = self._top_level_pks(work_section)
        self.assertNotIn(self.draft_page.pk, page_pks)
        self.assertIn(self.live_page.pk, page_pks)

    def test_sections_excludes_password_protected_pages(self):
        sections = self._get_sections()
        work_section = next(s for s in sections if s["section"].pk == self.section.pk)
        self.assertNotIn(self.private_page.pk, self._top_level_pks(work_section))

    def test_slug_is_always_sitemap(self):
        page = SitemapPage(title="My Sitemap", slug="wrong-slug")
        page.full_clean()
        self.assertEqual(page.slug, "sitemap")

    def test_duplicate_sitemap_page_raises_validation_error(self):
        from django.core.exceptions import ValidationError

        duplicate = SitemapPage(title="Another Sitemap", slug="sitemap")
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_sections_excludes_sitemap_page_itself(self):
        sections = self._get_sections()
        section_pks = [s["section"].pk for s in sections]
        self.assertNotIn(self.sitemap_page.pk, section_pks)

    def test_page_renders_200(self):
        response = self.client.get(self.sitemap_page.url)
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get(self.sitemap_page.url)
        self.assertTemplateUsed(response, "patterns/pages/sitemap/sitemap_page.html")

    def test_template_contains_section_class(self):
        response = self.client.get(self.sitemap_page.url)
        self.assertContains(response, "sitemap__section")
        self.assertContains(response, "sitemap__links")

    def test_link_anchor_text_equals_page_title(self):
        response = self.client.get(self.sitemap_page.url)
        self.assertContains(response, "Our Work")

    def test_sections_excludes_incident_slug_page(self):
        incident = StandardPageFactory(
            title="Incident", parent=self.home, slug="incident"
        )
        page = SitemapPage.objects.get(pk=self.sitemap_page.pk)
        section_pks = [s["section"].pk for s in page.sections]
        self.assertNotIn(incident.pk, section_pks)

    def test_sections_reflect_cms_state_across_requests(self):
        """
        Proves @cached_property is request-scoped. Each client.get() constructs
        a fresh SitemapPage instance from the database, so the sections list
        reflects the current CMS state per request — publish/unpublish changes
        are visible immediately on the next request.
        """
        response_before = self.client.get(self.sitemap_page.url)
        self.assertContains(response_before, self.live_page.title)

        # Unpublish the page — next request must not include it.
        self.live_page.unpublish()

        response_after = self.client.get(self.sitemap_page.url)
        self.assertNotContains(response_after, ">Our Work<")
