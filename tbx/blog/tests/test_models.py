from faker import Faker
from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.blog.models import BlogPage
from tbx.core.factories import HomePageFactory
from tbx.people.factories import AuthorFactory
from tbx.taxonomy.factories import ServiceFactory
from tbx.taxonomy.models import Service
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import (
    inline_formset,
    nested_form_data,
    rich_text,
    streamfield,
)

fake = Faker(["en_GB"])


class TestBlogIndexPageFactory(WagtailPageTestCase):
    def test_create(self):
        BlogIndexPageFactory()


class TestBlogPageFactory(WagtailPageTestCase):
    def test_create(self):
        blog_post = BlogPageFactory()
        self.assertEqual(blog_post.related_services.count(), 1)

        services = ServiceFactory.create_batch(size=3)
        another_blog_post = BlogPageFactory(related_services=list(services))
        self.assertEqual(another_blog_post.related_services.count(), 3)


class TestBlogPage(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        home_page = HomePageFactory(parent=root)

        site.root_page = home_page
        site.save()

        cls.blog_index = BlogIndexPageFactory(parent=home_page, title="Blog")

    def test_can_create_blog_page_with_supplied_post_data(self):
        service = ServiceFactory()
        author = AuthorFactory()
        self.login()
        self.assertCanCreate(
            self.blog_index,
            BlogPage,
            nested_form_data(
                {
                    "title": "Blog Page",
                    "date": fake.date_this_year(after_today=True),
                    "authors": inline_formset(
                        [
                            {"author": author.pk},
                        ]
                    ),
                    "related_links": inline_formset(
                        [
                            {
                                "title": fake.sentence(
                                    nb_words=3, variable_nb_words=False
                                ),
                                "link_external": fake.url(),
                            },
                        ]
                    ),
                    "related_services": service.pk,
                    "body": streamfield(
                        [
                            ("h2", "Here's a level 2 heading"),
                            (
                                "paragraph",
                                rich_text("<p>Here's a <em>short</em> paragraph</p>"),
                            ),
                        ]
                    ),
                }
            ),
        )

    def test_blog_page_is_routable(self):
        blog_page = BlogPageFactory(parent=self.blog_index, title="Test Blog Page")
        self.assertPageIsRoutable(blog_page)
        self.assertEqual(blog_page.url, "/blog/test-blog-page/")

    def test_related_blog_posts(self):
        """
        Tests the `related_blog_posts` property on the `BlogPage` model
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
