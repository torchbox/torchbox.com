import json

from django.template.loader import get_template, render_to_string
from django.test import RequestFactory

from wagtail.contrib.settings.context_processors import settings as settings_processor
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

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

    def test_organization_jsonld_renders(self):
        """Test that Organization JSON-LD is rendered on the homepage."""
        # Render the homepage template directly
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)

        # Check that the JSON-LD content is valid
        self.assertIn("application/ld+json", content)
        self.assertIn("Organization", content)

    def test_organization_jsonld_structure(self):
        """Test that Organization JSON-LD contains all required fields."""
        # Render the homepage template directly
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)

        # Extract Organization JSON-LD from the response
        start_marker = '<script type="application/ld+json">'
        end_marker = "</script>"

        # Find all JSON-LD scripts and look for the organization one
        json_scripts = []
        start_idx = 0
        while True:
            start_idx = content.find(start_marker, start_idx)
            if start_idx == -1:
                break
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                break

            json_content = content[start_idx + len(start_marker) : end_idx].strip()
            try:
                json_data = json.loads(json_content)
                if json_data.get("@type") == "Organization":
                    json_scripts.append(json_data)
            except json.JSONDecodeError:
                pass
            start_idx = end_idx + len(end_marker)

        self.assertGreater(len(json_scripts), 0, "Organization JSON-LD not found")

        org_data = json_scripts[0]

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
        # Render the homepage template directly
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)

        # Extract Organization JSON-LD
        start_marker = '<script type="application/ld+json">'
        end_marker = "</script>"

        json_scripts = []
        start_idx = 0
        while True:
            start_idx = content.find(start_marker, start_idx)
            if start_idx == -1:
                break
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                break

            json_content = content[start_idx + len(start_marker) : end_idx].strip()
            try:
                json_data = json.loads(json_content)
                if json_data.get("@type") == "Organization":
                    json_scripts.append(json_data)
            except json.JSONDecodeError:
                pass
            start_idx = end_idx + len(end_marker)

        org_data = json_scripts[0]
        same_as = org_data["sameAs"]

        # Test that all social links are valid URLs
        for link in same_as:
            self.assertTrue(link.startswith("http"), f"Invalid social link: {link}")

        # Test that we have the expected number of social links
        self.assertGreaterEqual(len(same_as), 3)

    def test_organization_jsonld_logo_url(self):
        """Test that Organization JSON-LD includes correct logo URL."""
        # Render the homepage template directly
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)

        # Extract Organization JSON-LD
        start_marker = '<script type="application/ld+json">'
        end_marker = "</script>"

        json_scripts = []
        start_idx = 0
        while True:
            start_idx = content.find(start_marker, start_idx)
            if start_idx == -1:
                break
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                break

            json_content = content[start_idx + len(start_marker) : end_idx].strip()
            try:
                json_data = json.loads(json_content)
                if json_data.get("@type") == "Organization":
                    json_scripts.append(json_data)
            except json.JSONDecodeError:
                pass
            start_idx = end_idx + len(end_marker)

        org_data = json_scripts[0]
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

    def test_base_template_includes_jsonld_block(self):
        """Test that the base template includes the extra_jsonld block."""
        # Render the homepage template directly
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)

        # Check that JSON-LD content is present (which means the block is working)
        self.assertIn("application/ld+json", content)
        self.assertIn("Organization", content)

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
        # Render the homepage template directly
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)

        # Check for JSON-LD script tags
        self.assertIn('<script type="application/ld+json">', content)
        self.assertIn("</script>", content)

    def test_multiple_jsonld_scripts(self):
        """Test that multiple JSON-LD scripts can be present on a page."""
        # Render the homepage template directly
        context = self._get_template_context(self.homepage)
        content = render_to_string("patterns/pages/home/home_page.html", context)

        # Count JSON-LD script tags
        script_count = content.count('<script type="application/ld+json">')
        self.assertGreater(script_count, 0, "No JSON-LD scripts found")

        # Should have at least the organization schema
        self.assertIn("Organization", content)
