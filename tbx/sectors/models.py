from wagtail.admin.panels import FieldPanel

from tbx.core.blocks import DynamicHeroBlock
from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField

from .blocks import SectorsIndexStoryBlock


class SectorsIndexPage(BasePage):
    """
    Umbrella landing page that lists the sectors Torchbox works in.

    Visually a sibling of DivisionPage — uses a copy of the division
    template and StreamBlock so the two page types can diverge
    independently. Children are DivisionPage and ServiceAreaPage (the
    two page types currently used as sector pages).
    """

    template = "patterns/pages/sectors/sectors_index_page.html"

    parent_page_types = ["torchbox.HomePage"]
    subpage_types = ["divisions.DivisionPage", "services.ServiceAreaPage"]

    hero = StreamField([("hero", DynamicHeroBlock())], max_num=1, min_num=1)
    body = StreamField(SectorsIndexStoryBlock(), blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("hero"),
        FieldPanel("body"),
    ]

    promote_panels = BasePage.promote_panels
