from faker import Faker
from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import HomePageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory
from tbx.taxonomy.models import Sector, Service
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

fake = Faker(["en_GB"])


class TestTaxonomies(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        cls.homepage = HomePageFactory(parent=root)

        # Create services
        cls.service_names = ["Service1", "Service2"]
        services = [ServiceFactory(name=name) for name in cls.service_names]

        # Create sectors
        cls.sector_names = ["Sector1", "Sector2"]
        sectors = [SectorFactory(name=name) for name in cls.sector_names]

        cls.blog_index_page = BlogIndexPageFactory(
            title="Blog Index Page",
            parent=cls.homepage,
        )

        cls.blog_page_both = BlogPageFactory(
            parent=cls.blog_index_page,
            related_services=[services[0]],
            related_sectors=[sectors[0]],
        )
        cls.blog_page_service = BlogPageFactory(
            parent=cls.blog_index_page, related_services=[services[1]]
        )
        cls.blog_page_sector = BlogPageFactory(
            parent=cls.blog_index_page, related_sectors=[sectors[1]]
        )

    def test_taxonomies_in_context(self):
        response = self.client.get(self.blog_index_page.url)

        self.assertEqual(response.status_code, 200)

        context = response.context

        # Check that the 'tags' variable is present in the context
        self.assertIn("tags", context)

        # Check that the 'tags' variable corresponds to all services and sectors used in child BlogPages
        expected_tags = [
            "Service1",
            "Service2",
            "Sector1",
            "Sector2",
        ]

        actual_tags = [tag.name for tag in context["tags"]]
        self.assertCountEqual(expected_tags, actual_tags)

    def test_blog_post_taxonomies_tags(self):
        """Tests that each blog_post only features the taxonomies associated with that page"""
        services = Service.objects.all()
        sectors = Sector.objects.all()

        self.assertListEqual(list(self.blog_page_both.tags), [services[0], sectors[0]])
        self.assertListEqual(list(self.blog_page_service.tags), [services[1]])
        self.assertListEqual(list(self.blog_page_sector.tags), [sectors[1]])

    def test_related_blog_posts_services(self):
        """
        Tests the `related_blog_posts` property on the `BlogPage` model using the Service taxonomy
        """

        blog_post1 = BlogPageFactory(
            related_services=[ServiceFactory(name="Lorem Ipsum")]
        )
        # there are no blog posts with related services that match those of blog_post1,
        # so there should be 0 related blog posts
        self.assertEqual(len(blog_post1.related_blog_posts), 0)

        blog_post2 = BlogPageFactory(
            related_services=[Service.objects.get(name="Service1")]
        )
        # There's only 1 blog post with the 'Culture' related service,
        # so there should only be 1 related blog post
        self.assertEqual(len(blog_post2.related_blog_posts), 1)

        blog_post3 = BlogPageFactory(
            related_services=list(Service.objects.filter(name__in=self.service_names)),
        )
        # There are 4 blog posts which share the 4 related services,
        # so there should be 3 related blog posts
        self.assertEqual(len(blog_post3.related_blog_posts), 3)

    def test_related_blog_posts_sectors(self):
        """
        Tests the `related_blog_posts` property on the `BlogPage` model using the Sectors taxonomy
        """

        blog_post1 = BlogPageFactory(
            related_sectors=[SectorFactory(name="Lorem Ipsum")]
        )
        # there are no blog posts with related sectors that match those of blog_post1,
        # so there should be 0 related blog posts
        self.assertEqual(len(blog_post1.related_blog_posts), 0)

        blog_post2 = BlogPageFactory(
            related_sectors=[Sector.objects.get(name="Sector1")]
        )
        # There's only 1 blog post with the 'Higher Education' related sectors,
        # so there should only be 1 related blog post
        self.assertEqual(len(blog_post2.related_blog_posts), 1)

        blog_post3 = BlogPageFactory(
            related_sectors=list(Sector.objects.filter(name__in=self.sector_names)),
        )
        # There are 4 blog posts which share the 3 related sectors,
        # so there should be 3 related blog posts
        self.assertEqual(len(blog_post3.related_blog_posts), 3)
