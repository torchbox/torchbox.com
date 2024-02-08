from django.test import Client

from faker import Faker
from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.taxonomy.models import Sector, Service
from wagtail.test.utils import WagtailPageTestCase

fake = Faker(["en_GB"])


class TestBlogIndexPageFactory(WagtailPageTestCase):
    def test_create(self):
        BlogIndexPageFactory()


class TestBlogIndexPage(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.blog_index_page = BlogIndexPageFactory(
            # parent=cls.homepage,
            title="Blog Index Page",
        )

        # Create services
        service_names = ["Service1", "Service2", "Service3"]
        services = [ServiceFactory(name=name) for name in service_names]

        # Create sectors
        sector_names = ["Sector1", "Sector2", "Sector3"]
        sectors = [SectorFactory(name=name) for name in sector_names]

        # Create BlogPage instances with various combinations of related services and sectors
        BlogPageFactory(
            parent=cls.blog_index_page,
            related_services=[services[0]],
            related_sectors=[sectors[0]],
        )
        BlogPageFactory(parent=cls.blog_index_page, related_services=[services[1]])
        BlogPageFactory(parent=cls.blog_index_page, related_sectors=[sectors[2]])

    def test_blog_index_page_tags_property(self):
        # Get the context from the BlogIndexPage's get_context method
        client = Client()
        # response = client.get(reverse(self.blog_index_page.url))
        response = client.get(self.blog_index_page.url)

        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Get the context from the response
        context = response.context

        # Check that the 'tags' variable is present in the context
        self.assertIn("tags", context)

        # Check that the 'tags' variable corresponds to all services and sectors used in child BlogPages
        expected_tags = [
            "Service1",
            "Service2",
            "Service3",
            "Sector1",
            "Sector2",
            "Sector3",
        ]
        actual_tags = [tag.name for tag in context["tags"]]
        self.assertCountEqual(expected_tags, actual_tags)


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
