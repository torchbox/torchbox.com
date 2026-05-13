from django.test import TestCase

from tbx.blog.factories import BlogPageFactory
from tbx.core.blocks import BlogChooserBlock, WorkChooserBlock, _resolve_chooser_pages
from tbx.work.factories import WorkPageFactory


class ResolveChooserPagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pages = WorkPageFactory.create_batch(3)

    def test_returns_live_public_pages_in_order(self):
        result = _resolve_chooser_pages(self.pages)
        self.assertListEqual(result, self.pages)

    def test_preserves_custom_order(self):
        reversed_pages = list(reversed(self.pages))
        result = _resolve_chooser_pages(reversed_pages)
        self.assertListEqual(result, reversed_pages)

    def test_drops_none_deleted_pages(self):
        pages_with_deleted = [None, self.pages[0], None, self.pages[1]]
        result = _resolve_chooser_pages(pages_with_deleted)
        self.assertListEqual(result, [self.pages[0], self.pages[1]])

    def test_drops_unpublished_pages(self):
        self.pages[0].unpublish()
        result = _resolve_chooser_pages(self.pages)
        self.assertListEqual(result, [self.pages[1], self.pages[2]])


class WorkChooserBlockTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pages = WorkPageFactory.create_batch(3)

    def test_block_context(self):
        block = WorkChooserBlock()

        context = block.get_context(
            {"featured_work_heading": "Featured Work", "work_pages": self.pages}
        )
        self.assertListEqual(context["work_pages"], self.pages)

        context = block.get_context(
            {
                "featured_work_heading": "Featured Work",
                "work_pages": [self.pages[2], self.pages[1], self.pages[0]],
            }
        )
        self.assertListEqual(
            context["work_pages"], [self.pages[2], self.pages[1], self.pages[0]]
        )

    def test_block_context_with_unpublished_pages(self):
        block = WorkChooserBlock()
        self.pages[0].unpublish()

        context = block.get_context(
            {"featured_work_heading": "Featured Work", "work_pages": self.pages}
        )
        self.assertListEqual(context["work_pages"], [self.pages[1], self.pages[2]])

    def test_block_context_with_deleted_pages(self):
        block = WorkChooserBlock()
        pages_with_deleted = [None, self.pages[0], self.pages[1]]

        context = block.get_context(
            {"featured_work_heading": "Featured Work", "work_pages": pages_with_deleted}
        )
        self.assertListEqual(context["work_pages"], [self.pages[0], self.pages[1]])


class BlogChooserBlockTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pages = BlogPageFactory.create_batch(3)

    def test_block_context(self):
        block = BlogChooserBlock()

        context = block.get_context(
            {"featured_blog_heading": "Featured Blog", "blog_pages": self.pages}
        )
        self.assertListEqual(context["blog_pages"], self.pages)

        context = block.get_context(
            {
                "featured_blog_heading": "Featured Blog",
                "blog_pages": [self.pages[2], self.pages[1], self.pages[0]],
            }
        )
        self.assertListEqual(
            context["blog_pages"], [self.pages[2], self.pages[1], self.pages[0]]
        )

    def test_block_context_with_unpublished_pages(self):
        block = BlogChooserBlock()
        self.pages[0].unpublish()

        context = block.get_context(
            {"featured_blog_heading": "Featured Blog", "blog_pages": self.pages}
        )
        self.assertListEqual(context["blog_pages"], [self.pages[1], self.pages[2]])

    def test_block_context_with_deleted_pages(self):
        block = BlogChooserBlock()
        pages_with_deleted = [None, self.pages[0], self.pages[1]]

        context = block.get_context(
            {
                "featured_blog_heading": "Featured Blog",
                "blog_pages": pages_with_deleted,
            }
        )
        self.assertListEqual(context["blog_pages"], [self.pages[0], self.pages[1]])
