from operator import attrgetter

from django.core.paginator import Page as PaginatorPage

from wagtail.coreutils import get_dummy_request
from wagtail.models import PageViewRestriction
from wagtail.test.utils import WagtailPageTestCase

from faker import Faker
from wagtail_factories import PageFactory

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.blog.models import BlogPage
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

    def test_related_blog_posts_same_division(self):
        sector = SectorFactory.create()
        # The logic of `final_division` skips ancestors with depth <= 2,
        # So we create the division page with enough parents to be at depth 3:
        division = DivisionPageFactory.create(parent=PageFactory(parent=PageFactory()))
        blog_post = BlogPageFactory(division=division, related_sectors=[sector])
        BlogPageFactory(title="same sector", division=None, related_sectors=[sector])
        BlogPageFactory(
            title="same division (direct)", division=division, related_sectors=[]
        )
        BlogPageFactory(
            title="same division (direct) same sector",
            division=division,
            related_sectors=[sector],
        )
        BlogPageFactory(title="same division (parent)", parent=division)

        self.assertQuerySetEqual(
            blog_post.related_blog_posts,
            [
                "same division (direct)",
                "same division (direct) same sector",
                "same division (parent)",
            ],
            transform=attrgetter("title"),
            ordered=False,
        )
