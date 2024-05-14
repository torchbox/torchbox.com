from django.test import TestCase

from tbx.core.blocks import WorkChooserBlock
from tbx.work.factories import WorkPageFactory


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
