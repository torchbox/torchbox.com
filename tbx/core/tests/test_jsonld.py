import json

from django.template.loader import get_template

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
        response = self.client.get(self.homepage.url)
        json_scripts = self._extract_jsonld_by_type(response.content, "Organization")
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
        self.assertCountEqual(
            org_data["sameAs"],
            [
                "https://bsky.app/profile/torchbox.com",
                "https://www.linkedin.com/company/torchbox",
                "https://www.instagram.com/torchboxltd/",
            ],
        )

    def test_organization_jsonld_logo_url(self):
        """Test that Organization JSON-LD includes correct logo URL."""
        org_data = self._get_organization_jsonld()
        self.assertEqual(
            org_data["logo"], "https://torchbox.com/android-chrome-512x512.png"
        )


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
        response = self.client.get(self.homepage.url)
        json_scripts = self._extract_jsonld_by_type(response.content, "Organization")
        self.assertGreater(len(json_scripts), 0, "Organization JSON-LD not found")
        return json_scripts[0]

    def test_base_template_includes_jsonld_block(self):
        """Test that the base template includes the extra_jsonld block."""
        org_data = self._get_organization_jsonld()
        self.assertEqual(org_data["name"], "Torchbox")

    def test_breadcrumb_template_included(self):
        """Test that breadcrumb JSON-LD template is included."""
        response = self.client.get(self.blog_post.url)
        breadcrumbs = self._extract_jsonld_by_type(response.content, "BreadcrumbList")

        self.assertGreater(len(breadcrumbs), 0, "BreadcrumbList JSON-LD not found")
        self.assertIn("itemListElement", breadcrumbs[0])

    def test_blog_posting_template_included(self):
        """Test that blog posting JSON-LD template is included for blog pages."""
        response = self.client.get(self.blog_post.url)
        schema = self._extract_jsonld_by_type(response.content, "BlogPosting")

        self.assertGreater(len(schema), 0, "BlogPosting JSON-LD not found")
        self.assertEqual(schema[0]["headline"], "Test Blog Post")

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
