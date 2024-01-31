from django.utils.text import slugify

from bs4 import BeautifulSoup
from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import HomePageFactory, StandardPageFactory
from tbx.core.utils.models import ColourTheme
from tbx.work.factories import (
    HistoricalWorkPageFactory,
    WorkIndexPageFactory,
    WorkPageFactory,
)
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase


class TestColourTheme(WagtailPageTestCase):
    def setUp(self):
        super().setUp()

        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        self.home = HomePageFactory(parent=root)

        site.root_page = self.home
        site.save()

        self.blogindex = BlogIndexPageFactory(title="Blog", parent=self.home)
        self.workindex = WorkIndexPageFactory(title="Work", parent=self.home)

    def test_no_theme_applied(self):
        for page in [self.home, self.blogindex, self.workindex]:
            self.assertEqual(page.theme_class, ColourTheme.NONE)

        blog = BlogPageFactory(parent=self.blogindex)
        self.assertEqual(blog.theme_class, ColourTheme.NONE)

        work = WorkPageFactory(parent=self.workindex)
        self.assertEqual(work.theme_class, ColourTheme.NONE)

        std_page = StandardPageFactory(parent=work)
        self.assertEqual(std_page.theme_class, ColourTheme.NONE)

        # -------------------------------------------
        # Now we check the templates for css classes
        # -------------------------------------------

        for page in [self.home, self.blogindex, self.workindex, work, blog, std_page]:
            class_suffix = slugify(page.get_verbose_name())
            response = self.client.get(page.url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Get the list of classes on the html tag
            html_classes = soup.find("html").get("class", [])

            # Check if the specified class is the only class present
            self.assertEqual(len(html_classes), 1)
            self.assertEqual(html_classes[0], f"template-{class_suffix}")

    def test_theme_on_homepage(self):
        self.home.theme = ColourTheme.CORAL
        self.home.save()
        self.home.refresh_from_db()

        self.assertEqual(self.home.theme_class, ColourTheme.CORAL)
        self.assertEqual(self.blogindex.theme_class, ColourTheme.CORAL)
        self.assertEqual(self.workindex.theme_class, ColourTheme.CORAL)

        blog = BlogPageFactory(parent=self.blogindex)
        self.assertEqual(blog.theme_class, ColourTheme.CORAL)

        work = WorkPageFactory(parent=self.workindex)
        self.assertEqual(work.theme_class, ColourTheme.CORAL)

        std_page = StandardPageFactory(parent=work)
        self.assertEqual(std_page.theme_class, ColourTheme.CORAL)

        # -------------------------------------------
        # Now we check the templates for css classes
        # -------------------------------------------

        for page in [self.home, self.blogindex, self.workindex, work, blog, std_page]:
            class_suffix = slugify(page.get_verbose_name())
            response = self.client.get(page.url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Get the list of classes on the html tag
            html_classes = soup.find("html").get("class", [])

            # Check that we have the correct classes applied
            self.assertEqual(len(html_classes), 2)
            self.assertEqual(html_classes[0], f"template-{class_suffix}")
            self.assertEqual(html_classes[1], ColourTheme.CORAL)

    def test_theme_on_an_indexpage(self):
        self.blogindex.theme = ColourTheme.LAGOON
        self.blogindex.save()
        self.blogindex.refresh_from_db()

        self.assertEqual(self.home.theme_class, ColourTheme.NONE)
        self.assertEqual(self.blogindex.theme_class, ColourTheme.LAGOON)

        # child of blogindex
        blog = BlogPageFactory(parent=self.blogindex)
        self.assertEqual(blog.theme_class, ColourTheme.LAGOON)

        # grandchild of blogindex
        std_page = StandardPageFactory(parent=blog)
        self.assertEqual(std_page.theme_class, ColourTheme.LAGOON)

        # -------------------------------------------
        # Now we check the templates for css classes
        # -------------------------------------------

        for page in [self.home, self.workindex]:
            class_suffix = slugify(page.get_verbose_name())
            response = self.client.get(page.url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Get the list of classes on the html tag
            html_classes = soup.find("html").get("class", [])

            # Check if the specified class is the only class present
            self.assertEqual(len(html_classes), 1)
            self.assertEqual(html_classes[0], f"template-{class_suffix}")

        for page in [self.blogindex, blog, std_page]:
            class_suffix = slugify(page.get_verbose_name())
            response = self.client.get(page.url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Get the list of classes on the html tag
            html_classes = soup.find("html").get("class", [])

            # Check that we have the correct classes applied
            self.assertEqual(len(html_classes), 2)
            self.assertEqual(html_classes[0], f"template-{class_suffix}")
            self.assertEqual(html_classes[1], ColourTheme.LAGOON)

    def test_custom_theme_on_descendants(self):
        self.workindex.theme = ColourTheme.BANANA
        self.workindex.save()
        self.workindex.refresh_from_db()

        self.assertEqual(self.home.theme_class, ColourTheme.NONE)
        self.assertEqual(self.blogindex.theme_class, ColourTheme.NONE)
        self.assertEqual(self.workindex.theme_class, ColourTheme.BANANA)

        # child of workindex
        work = HistoricalWorkPageFactory(parent=self.workindex)
        self.assertEqual(work.theme_class, ColourTheme.BANANA)

        # another child of workindex, this time we set the theme
        morework = HistoricalWorkPageFactory(parent=self.workindex)
        morework.theme = ColourTheme.CORAL
        morework.save()
        morework.refresh_from_db()
        self.assertEqual(morework.theme_class, ColourTheme.CORAL)
        # sibling shouldn't be affected
        self.assertEqual(work.theme_class, ColourTheme.BANANA)
        # parent shouldn't be affected
        self.assertEqual(self.workindex.theme_class, ColourTheme.BANANA)

        # child of morework
        std_page = StandardPageFactory(parent=morework)
        # should inherit parent's theme
        self.assertEqual(std_page.theme_class, ColourTheme.CORAL)

        # -------------------------------------------
        # Now we check the templates for css classes
        # -------------------------------------------

        for page in [self.home, self.blogindex]:
            class_suffix = slugify(page.get_verbose_name())
            response = self.client.get(page.url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Get the list of classes on the html tag
            html_classes = soup.find("html").get("class", [])

            # Check if the specified class is the only class present
            self.assertEqual(len(html_classes), 1)
            self.assertEqual(html_classes[0], f"template-{class_suffix}")

        for page in [self.workindex, work]:
            class_suffix = slugify(page.get_verbose_name())
            response = self.client.get(page.url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Get the list of classes on the html tag
            html_classes = soup.find("html").get("class", [])

            # Check that we have the correct classes applied
            self.assertEqual(len(html_classes), 2)
            self.assertEqual(html_classes[0], f"template-{class_suffix}")
            self.assertEqual(html_classes[1], ColourTheme.BANANA)

        for page in [morework, std_page]:
            class_suffix = slugify(page.get_verbose_name())
            response = self.client.get(page.url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Get the list of classes on the html tag
            html_classes = soup.find("html").get("class", [])

            # Check that we have the correct classes applied
            self.assertEqual(len(html_classes), 2)
            self.assertEqual(html_classes[0], f"template-{class_suffix}")
            self.assertEqual(html_classes[1], ColourTheme.CORAL)
