from faker import Faker
from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.taxonomy.models import Sector, Service
from wagtail.test.utils import WagtailPageTestCase

fake = Faker(["en_GB"])


class TestBlogIndexPageFactory(WagtailPageTestCase):
    def test_create(self):
        BlogIndexPageFactory()


class TestBlogPageFactory(WagtailPageTestCase):
    def test_create_services(self):
        blog_post = BlogPageFactory()
        self.assertEqual(blog_post.related_services.count(), 1)

        services = ServiceFactory.create_batch(size=3)
        another_blog_post = BlogPageFactory(related_services=list(services))
        self.assertEqual(another_blog_post.related_services.count(), 3)

    def test_create_sectors(self):
        blog_post = BlogPageFactory()
        self.assertEqual(blog_post.related_services.count(), 1)

        sectors = SectorFactory.create_batch(size=3)
        another_blog_post = BlogPageFactory(related_sectors=list(sectors))
        self.assertEqual(another_blog_post.related_sectors.count(), 3)


class TestBlogPage(WagtailPageTestCase):
    def test_related_blog_posts_services(self):
        """
        Tests the `related_blog_posts` property on the `BlogPage` model using the Service taxonomy
        """
        service_names = [
            "Culture",
            "Digital products",
            "Email marketing",
            "Social media",
        ]
        for name in service_names:
            service = ServiceFactory(name=name)
            BlogPageFactory(related_services=[service])

        blog_post1 = BlogPageFactory(
            related_services=[ServiceFactory(name="Lorem Ipsum")]
        )
        # there are no blog posts with related services that match those of blog_post1,
        # so there should be 0 related blog posts
        self.assertEqual(len(blog_post1.related_blog_posts), 0)

        blog_post2 = BlogPageFactory(
            related_services=[Service.objects.get(name="Culture")]
        )
        # There's only 1 blog post with the 'Culture' related service,
        # so there should only be 1 related blog post
        self.assertEqual(len(blog_post2.related_blog_posts), 1)

        blog_post3 = BlogPageFactory(
            related_services=list(Service.objects.filter(name__in=service_names)),
        )
        # There are 4 blog posts which share the 4 related services,
        # so there should be 3 related blog posts
        self.assertEqual(len(blog_post3.related_blog_posts), 3)

    def test_related_blog_posts_sectors(self):
        """
        Tests the `related_blog_posts` property on the `BlogPage` model using the Sectors taxonomy
        """
        sector_names = [
            "Higher Education",
            "Not-for-profit",
            "Public Sector",
        ]
        for name in sector_names:
            sectors = SectorFactory(name=name)
            BlogPageFactory(related_sectors=[sectors])

        blog_post1 = BlogPageFactory(
            related_sectors=[SectorFactory(name="Lorem Ipsum")]
        )
        # there are no blog posts with related sectors that match those of blog_post1,
        # so there should be 0 related blog posts
        self.assertEqual(len(blog_post1.related_blog_posts), 0)

        blog_post2 = BlogPageFactory(
            related_sectors=[Sector.objects.get(name="Higher Education")]
        )
        # There's only 1 blog post with the 'Higher Education' related sectors,
        # so there should only be 1 related blog post
        self.assertEqual(len(blog_post2.related_blog_posts), 1)

        blog_post3 = BlogPageFactory(
            related_sectors=list(Sector.objects.filter(name__in=sector_names)),
        )
        # There are 4 blog posts which share the 3 related sectors,
        # so there should be 3 related blog posts
        self.assertEqual(len(blog_post3.related_blog_posts), 3)
