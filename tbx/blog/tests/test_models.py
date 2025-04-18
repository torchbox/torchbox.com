from operator import attrgetter

from django.core.paginator import Page as PaginatorPage

from wagtail.coreutils import get_dummy_request
from wagtail.models import PageViewRestriction, Site
from wagtail.test.utils import WagtailPageTestCase

from faker import Faker

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.blog.models import BlogPage
from tbx.core.factories import HomePageFactory
from tbx.divisions.factories import DivisionPageFactory
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

    def test_tags_not_rendered(self):
        page = BlogPageFactory(
            parent=self.blog_index,
            related_services=[ServiceFactory(name="SHOULD_NOT_BE_RENDERED")],
            related_sectors=[SectorFactory(name="SHOULD_NOT_BE_RENDERED")],
        )
        response = self.client.get(page.url)
        self.assertNotContains(response, "SHOULD_NOT_BE_RENDERED")
