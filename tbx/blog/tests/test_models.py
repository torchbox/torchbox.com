from faker import Faker
from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from wagtail.test.utils import WagtailPageTestCase

fake = Faker(["en_GB"])


class TestBlogIndexPageFactory(WagtailPageTestCase):
    def test_create(self):
        BlogIndexPageFactory()


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
