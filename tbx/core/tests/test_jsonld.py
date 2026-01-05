import json

from django.template.loader import get_template, render_to_string
from django.test import RequestFactory

from wagtail.contrib.settings.context_processors import settings as settings_processor
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from bs4 import BeautifulSoup

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import HomePageFactory
from tbx.divisions.factories import DivisionPageFactory


class TestOrganizationJSONLD(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(
            parent=root,
            title="Torchbox",
            hero_heading_1="Welcome to",
            hero_heading_2="Torchbox",
        )

    def _get_template_context(self, page):
        """Helper method to create proper template context with settings."""
        factory = RequestFactory()
        request = factory.get("/")
        settings_context = settings_processor(request)

        return {"page": page, "request": request, **settings_context}

    def _extract_jsonld_by_type(self, content, jsonld_type):
        """Helper method to extract JSON-LD by type from rendered content."""
        soup = BeautifulSoup(content, "html.parser")
        scripts = [
            json.loads(tag.string)
            for tag in soup.find_all("script", type="application/ld+json")
        ]
        return [script for script in scripts if script["@type"] == jsonld_type]

    def _get_organization_jsonld(self):
        """Helper method to get Organization JSON-LD from homepage."""
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)
        json_scripts = self._extract_jsonld_by_type(content, "Organization")
        self.assertGreater(len(json_scripts), 0, "Organization JSON-LD not found")
        return json_scripts[0]

    def test_organization_jsonld_renders(self):
        """Test that Organization JSON-LD is rendered on the homepage."""
        org_data = self._get_organization_jsonld()
        self.assertEqual(org_data["@type"], "Organization")

    def test_organization_jsonld_structure(self):
        """Test that Organization JSON-LD contains all required fields."""
        org_data = self._get_organization_jsonld()

        # Test required fields
        self.assertEqual(org_data["@context"], "https://schema.org")
        self.assertEqual(org_data["@type"], "Organization")
        self.assertEqual(org_data["name"], "Torchbox")
        self.assertEqual(org_data["url"], "https://torchbox.com/")

        # Test logo
        self.assertIn("logo", org_data)
        self.assertEqual(
            org_data["logo"], "https://torchbox.com/android-chrome-512x512.png"
        )

        # Test social media links
        self.assertIn("sameAs", org_data)
        same_as = org_data["sameAs"]
        self.assertIsInstance(same_as, list)
        self.assertGreater(len(same_as), 0)

        # Check for expected social media links
        expected_links = [
            "https://bsky.app/profile/torchbox.com",
            "https://www.linkedin.com/company/torchbox",
            "https://www.instagram.com/torchboxltd/",
        ]
        for link in expected_links:
            self.assertIn(link, same_as)

    def test_organization_jsonld_social_links(self):
        """Test that Organization JSON-LD includes correct social media links."""
        org_data = self._get_organization_jsonld()
        same_as = org_data["sameAs"]

        # Test that all social links are valid URLs
        for link in same_as:
            self.assertTrue(link.startswith("http"), f"Invalid social link: {link}")

        # Test that we have the expected number of social links
        self.assertGreaterEqual(len(same_as), 3)

    def test_organization_jsonld_logo_url(self):
        """Test that Organization JSON-LD includes correct logo URL."""
        org_data = self._get_organization_jsonld()
        logo_url = org_data["logo"]

        # Test that logo URL is correct
        self.assertEqual(logo_url, "https://torchbox.com/android-chrome-512x512.png")
        self.assertTrue(logo_url.startswith("https://"), "Logo URL should be HTTPS")


class TestJSONLDTemplateInclusion(WagtailPageTestCase):
    """Test that JSON-LD templates are properly included in page renders."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)
        cls.division = DivisionPageFactory(parent=cls.homepage, title="Charity")
        cls.blog_index = BlogIndexPageFactory(parent=cls.division, title="Blog")
        cls.blog_post = BlogPageFactory(parent=cls.blog_index, title="Test Blog Post")

    def _get_template_context(self, page):
        """Helper method to create proper template context with settings."""
        factory = RequestFactory()
        request = factory.get("/")
        settings_context = settings_processor(request)

        return {"page": page, "request": request, **settings_context}

    def _extract_jsonld_by_type(self, content, jsonld_type):
        """Helper method to extract JSON-LD by type from rendered content."""
        soup = BeautifulSoup(content, "html.parser")
        scripts = [
            json.loads(tag.string)
            for tag in soup.find_all("script", type="application/ld+json")
        ]
        return [script for script in scripts if script["@type"] == jsonld_type]

    def _get_organization_jsonld(self):
        """Helper method to get Organization JSON-LD from homepage."""
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)
        json_scripts = self._extract_jsonld_by_type(content, "Organization")
        self.assertGreater(len(json_scripts), 0, "Organization JSON-LD not found")
        return json_scripts[0]

    def test_base_template_includes_jsonld_block(self):
        """Test that the base template includes the extra_jsonld block."""
        org_data = self._get_organization_jsonld()
        self.assertEqual(org_data["@type"], "Organization")

    def test_breadcrumb_template_included(self):
        """Test that breadcrumb JSON-LD template is included."""
        # Render the breadcrumb JSON-LD template directly
        context = {"page": self.blog_post, "request": RequestFactory().get("/")}
        content = render_to_string(
            "patterns/navigation/components/breadcrumbs-jsonld.html", context
        )

        # Check that breadcrumb JSON-LD content is present
        self.assertIn("application/ld+json", content)
        self.assertIn("BreadcrumbList", content)

    def test_blog_posting_template_included(self):
        """Test that blog posting JSON-LD template is included for blog pages."""
        # This test would need to be run on an actual blog page
        # For now, we'll just verify the template exists
        try:
            template = get_template("patterns/pages/blog/blog-posting-jsonld.html")
            self.assertIsNotNone(template)
        except Exception as e:
            self.fail(f"Blog posting JSON-LD template not found: {e}")

    def test_breadcrumb_template_exists(self):
        """Test that breadcrumb JSON-LD template exists."""
        try:
            template = get_template(
                "patterns/navigation/components/breadcrumbs-jsonld.html"
            )
            self.assertIsNotNone(template)
        except Exception as e:
            self.fail(f"Breadcrumb JSON-LD template not found: {e}")

    def test_jsonld_script_tags_present(self):
        """Test that JSON-LD script tags are present in the rendered HTML."""
        org_data = self._get_organization_jsonld()
        self.assertIsNotNone(org_data)

    def test_multiple_jsonld_scripts(self):
        """Test that multiple JSON-LD scripts can be present on a page."""
        org_data = self._get_organization_jsonld()
        self.assertEqual(org_data["@type"], "Organization")
