from faker import Faker
from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.blog.models import BlogIndexPage, BlogPage
from tbx.core.factories import HomePageFactory
from tbx.core.models import HomePage
from tbx.people.factories import AuthorFactory
from tbx.taxonomy.factories import ServiceFactory
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import (
    inline_formset,
    nested_form_data,
    rich_text,
    streamfield,
)

fake = Faker(["en_GB"])


class TestBlogPageFactory(WagtailPageTestCase):
    def test_create(self):
        BlogPageFactory()


class TestBlogIndexPageFactory(WagtailPageTestCase):
    def test_create(self):
        BlogIndexPageFactory()


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

    def test_can_create_blog_page_under_blog_index_page(self):
        self.assertCanCreateAt(BlogIndexPage, BlogPage)

    def test_cannot_create_blog_page_under_home_page(self):
        self.assertCanNotCreateAt(HomePage, BlogPage)

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
