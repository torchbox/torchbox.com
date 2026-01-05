import json
from operator import attrgetter

from django.core.paginator import Page as PaginatorPage
from django.template.loader import render_to_string

from wagtail.coreutils import get_dummy_request
from wagtail.models import PageViewRestriction, Site
from wagtail.test.utils import WagtailPageTestCase

from bs4 import BeautifulSoup
from faker import Faker

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.blog.models import BlogPage
from tbx.core.factories import HomePageFactory
from tbx.core.utils.models import PageAuthor
from tbx.divisions.factories import DivisionPageFactory
from tbx.images.factories import CustomImageFactory
from tbx.people.factories import AuthorFactory, PersonPageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory


fake = Faker(["en_GB"])


class TestBlogIndexPageFactory(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.blog_index = BlogIndexPageFactory(title="The Torchbox Blog")
        cls.blog_post = BlogPageFactory(title="The blog post", parent=cls.blog_index)
        cls.private_blog_post = BlogPageFactory(
            title="Private blog post", parent=cls.blog_index
        )
        cls.draft_blog_post = BlogPageFactory(
            title="Draft blog post", live=False, parent=cls.blog_index
        )
        PageViewRestriction.objects.create(
            page=cls.private_blog_post,
            restriction_type="password",
            password="password123",  # noqa: S106
        )

    def test_get_context(self):
        context = self.blog_index.get_context(get_dummy_request())
        blog_posts = context["blog_posts"]
        self.assertIsInstance(blog_posts, PaginatorPage)
        self.assertEqual(blog_posts.object_list.first(), self.blog_post)

    def test_blog_posts_property(self):
        """Checks that the blog_posts property returns public and published blog posts under the given blog index."""
        another_blog = BlogIndexPageFactory(title="Tech blog")
        BlogPageFactory(title="Tech blog", parent=another_blog)
        self.assertQuerySetEqual(
            self.blog_index.blog_posts, BlogPage.objects.filter(pk=self.blog_post.pk)
        )


class TestBlogPageFactory(WagtailPageTestCase):
    def test_create(self):
        blog_post = BlogPageFactory()
        self.assertEqual(blog_post.related_services.count(), 0)
        self.assertEqual(blog_post.related_sectors.count(), 0)

        services = ServiceFactory.create_batch(size=3)
        sectors = SectorFactory.create_batch(size=2)
        another_blog_post = BlogPageFactory(
            related_services=list(services), related_sectors=list(sectors)
        )
        self.assertEqual(another_blog_post.related_services.count(), 3)
        self.assertEqual(another_blog_post.related_sectors.count(), 2)


class TestBlogPage(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)
        cls.division = DivisionPageFactory(parent=cls.homepage, title="Charity")
        cls.blog_index = BlogIndexPageFactory(parent=cls.division)
        cls.other_division = DivisionPageFactory(parent=cls.homepage, title="Public")
        cls.other_index = BlogIndexPageFactory(parent=cls.other_division)

    def test_related_blog_posts(self):
        BlogPageFactory(parent=self.other_index)

        blog_post = BlogPageFactory(parent=self.blog_index, title="Blog Post 1")
        BlogPageFactory(parent=self.blog_index, title="Blog Post 2", date="2025-01-01")
        BlogPageFactory(parent=self.blog_index, title="Blog Post 3", date="2025-01-02")

        self.assertQuerySetEqual(
            blog_post.related_blog_posts,
            [
                "Blog Post 3",
                "Blog Post 2",
            ],
            transform=attrgetter("title"),
        )

    def test_related_blog_posts_manually_set(self):
        blog_post = BlogPageFactory(
            parent=self.blog_index,
            title="Blog Post 1",
        )
        for i in [2, 3, 4]:
            blog_post.related_posts.create(
                page=BlogPageFactory(title=f"Blog Post {i}", date=f"2025-01-{i:02}"),
            )

        self.assertQuerySetEqual(
            blog_post.related_blog_posts,
            [
                "Blog Post 4",
                "Blog Post 3",
                "Blog Post 2",
            ],
            transform=attrgetter("title"),
        )

    def test_related_blog_posts_padded_if_not_enough(self):
        blog_post = BlogPageFactory(
            parent=self.blog_index,
            title="Blog Post 1",
        )
        blog_post.related_posts.create(
            page=BlogPageFactory(title="Blog Post 2", date="2025-01-01")
        )
        BlogPageFactory(parent=self.blog_index, title="Blog Post 3", date="2025-01-02")
        BlogPageFactory(parent=self.blog_index, title="Blog Post 4", date="2025-01-03")

        self.assertQuerySetEqual(
            blog_post.related_blog_posts,
            [
                "Blog Post 2",  # Comes first because selected manually
                "Blog Post 4",
                "Blog Post 3",
            ],
            transform=attrgetter("title"),
        )


class TestBlogPageJSONLD(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)
        cls.division = DivisionPageFactory(parent=cls.homepage, title="Charity")
        cls.blog_index = BlogIndexPageFactory(parent=cls.division)

        # Create a person page for the author
        cls.author = PersonPageFactory(parent=cls.homepage, title="John Doe")

        # Create a blog post with all the necessary fields for JSON-LD
        cls.blog_post = BlogPageFactory(
            parent=cls.blog_index,
            title="Test Blog Post",
            date="2024-01-15",
            listing_summary="This is a test blog post summary",
            search_description="SEO description for the blog post",
        )

        # Publish the blog post properly
        cls.blog_post.save_revision().publish()

        # Create an Author instance linked to the PersonPage
        author = AuthorFactory(person_page=cls.author, name="John Doe")

        # Add author to the blog post
        PageAuthor.objects.create(page=cls.blog_post, author=author)

    def _extract_jsonld(self, content):
        """Helper method to extract JSON-LD from rendered content."""
        soup = BeautifulSoup(content, "html.parser")
        scripts = soup.find_all("script", type="application/ld+json")
        return [json.loads(tag.string) for tag in scripts]

    def test_blog_posting_jsonld_renders(self):
        """Test that BlogPosting JSON-LD is rendered in the blog detail template."""
        # Render the blog posting JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/pages/blog/blog-posting-jsonld.html", context
        )

        # Check that the JSON-LD content is valid
        self.assertIn("application/ld+json", jsonld_content)
        self.assertIn("BlogPosting", jsonld_content)

        # Parse the JSON to ensure it's valid
        scripts = self._extract_jsonld(jsonld_content)
        self.assertGreater(len(scripts), 0, "JSON-LD script tag not found")
        self.assertEqual(scripts[0]["@type"], "BlogPosting")

    def test_blog_posting_jsonld_structure(self):
        """Test that BlogPosting JSON-LD contains all required fields."""
        # Render the blog posting JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/pages/blog/blog-posting-jsonld.html", context
        )

        # Extract JSON-LD from the response
        scripts = self._extract_jsonld(jsonld_content)
        self.assertGreater(len(scripts), 0, "JSON-LD script tag not found")
        json_data = scripts[0]

        # Test required fields
        self.assertEqual(json_data["@context"], "https://schema.org")
        self.assertEqual(json_data["@type"], "BlogPosting")
        self.assertEqual(json_data["headline"], "Test Blog Post")
        self.assertEqual(json_data["datePublished"], "2024-01-15")

        # Test mainEntityOfPage
        self.assertIn("mainEntityOfPage", json_data)
        self.assertEqual(json_data["mainEntityOfPage"]["@type"], "WebPage")

        # Test publisher
        self.assertIn("publisher", json_data)
        self.assertEqual(json_data["publisher"]["@type"], "Organization")
        self.assertEqual(json_data["publisher"]["name"], "Torchbox")

        # Test author
        self.assertIn("author", json_data)
        self.assertEqual(json_data["author"]["@type"], "Person")
        self.assertEqual(json_data["author"]["name"], "John Doe")

    def test_blog_posting_jsonld_with_feed_image(self):
        """Test BlogPosting JSON-LD includes image when feed_image is set."""
        # Create an image for the blog post
        image = CustomImageFactory()
        self.blog_post.feed_image = image
        self.blog_post.save()

        # Render the blog posting JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/pages/blog/blog-posting-jsonld.html", context
        )

        # Extract JSON-LD
        scripts = self._extract_jsonld(jsonld_content)
        json_data = scripts[0]

        # Test that image is included
        self.assertIn("image", json_data)
        self.assertIn("format-webp", json_data["image"])

    def test_blog_posting_jsonld_without_feed_image(self):
        """Test BlogPosting JSON-LD works without feed_image."""
        self.blog_post.feed_image = None
        self.blog_post.save()

        # Render the blog posting JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/pages/blog/blog-posting-jsonld.html", context
        )

        # Extract JSON-LD
        scripts = self._extract_jsonld(jsonld_content)
        json_data = scripts[0]

        # Test that image is not included
        self.assertNotIn("image", json_data)

    def test_blog_posting_jsonld_description_fallback(self):
        """Test that description falls back to listing_summary when search_description is not set."""
        self.blog_post.search_description = ""
        self.blog_post.save()

        # Render the blog posting JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/pages/blog/blog-posting-jsonld.html", context
        )

        # Extract JSON-LD
        scripts = self._extract_jsonld(jsonld_content)
        json_data = scripts[0]

        # Test that description uses listing_summary as fallback
        self.assertEqual(json_data["description"], "This is a test blog post summary")

    def test_blog_posting_jsonld_date_modified(self):
        """Test that dateModified is set correctly."""
        # Update the blog post to trigger last_published_at
        self.blog_post.title = "Updated Title"
        self.blog_post.save()

        # Render the blog posting JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/pages/blog/blog-posting-jsonld.html", context
        )

        # Extract JSON-LD
        scripts = self._extract_jsonld(jsonld_content)
        json_data = scripts[0]

        # Test that dateModified is present
        self.assertIn("dateModified", json_data)
        # Should be in YYYY-MM-DD format
        self.assertRegex(json_data["dateModified"], r"^\d{4}-\d{2}-\d{2}$")


class TestBreadcrumbJSONLD(WagtailPageTestCase):
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

    def test_breadcrumb_jsonld_renders(self):
        """Test that breadcrumb JSON-LD is rendered in the blog detail template."""
        # Render the breadcrumb JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/navigation/components/breadcrumbs-jsonld.html", context
        )

        # Check that the JSON-LD content is valid
        self.assertIn("application/ld+json", jsonld_content)
        self.assertIn("BreadcrumbList", jsonld_content)

    def test_breadcrumb_jsonld_structure(self):
        """Test that breadcrumb JSON-LD contains correct structure."""
        # Render the breadcrumb JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/navigation/components/breadcrumbs-jsonld.html", context
        )

        # Extract breadcrumb JSON-LD from the response
        json_scripts = self._extract_jsonld_by_type(jsonld_content, "BreadcrumbList")
        self.assertGreater(len(json_scripts), 0, "BreadcrumbList JSON-LD not found")

        breadcrumb_data = json_scripts[0]

        # Test required fields
        self.assertEqual(breadcrumb_data["@context"], "https://schema.org/")
        self.assertEqual(breadcrumb_data["@type"], "BreadcrumbList")
        self.assertIn("itemListElement", breadcrumb_data)

        # Test that we have the expected breadcrumb items
        items = breadcrumb_data["itemListElement"]
        self.assertGreater(len(items), 0, "No breadcrumb items found")

        # Test first item (should be Charity based on the breadcrumb structure)
        first_item = items[0]
        self.assertEqual(first_item["@type"], "ListItem")
        self.assertEqual(first_item["position"], 1)
        self.assertEqual(first_item["name"], "Charity")

        # Test that all items have required fields
        for i, item in enumerate(items):
            self.assertEqual(item["@type"], "ListItem")
            self.assertEqual(item["position"], i + 1)
            self.assertIn("name", item)
            self.assertIn("item", item)

    def test_breadcrumb_jsonld_with_division(self):
        """Test breadcrumb JSON-LD includes division page."""
        # Render the breadcrumb JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/navigation/components/breadcrumbs-jsonld.html", context
        )

        # Extract breadcrumb JSON-LD
        json_scripts = self._extract_jsonld_by_type(jsonld_content, "BreadcrumbList")
        breadcrumb_data = json_scripts[0]
        items = breadcrumb_data["itemListElement"]

        # Should have at least Division and Blog Index
        self.assertGreaterEqual(len(items), 2)

        # Check that division is included
        division_names = [item["name"] for item in items]
        self.assertIn("Charity", division_names)

    def test_breadcrumb_jsonld_urls(self):
        """Test that breadcrumb JSON-LD contains URL structure."""
        # Render the breadcrumb JSON-LD template directly
        context = {"page": self.blog_post}
        jsonld_content = render_to_string(
            "patterns/navigation/components/breadcrumbs-jsonld.html", context
        )

        # Extract breadcrumb JSON-LD
        json_scripts = self._extract_jsonld_by_type(jsonld_content, "BreadcrumbList")
        breadcrumb_data = json_scripts[0]
        items = breadcrumb_data["itemListElement"]

        # Test that all items have item field (URL structure)
        for item in items:
            self.assertIn("item", item)
            # In test environment, URLs might be None, so just check the field exists
            self.assertIsNotNone(item["item"])
