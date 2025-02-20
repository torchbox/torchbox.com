from django.db import models

from wagtail.admin.panels import FieldPanel

from tbx.core.blocks import DynamicHeroBlock
from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField

from .blocks import DivisionStoryBlock


class DivisionPage(BasePage):
    template = "patterns/pages/divisions/division_page.html"

    parent_page_types = ["torchbox.HomePage"]

    class Logo(models.TextChoices):
        TORCHBOX = "logo-torchbox", "Torchbox"
        CHARITY = "logo-charity", "Torchbox Charity"
        PUBLIC = "logo-public", "Torchbox Public"
        WAGTAIL = "logo-wagtail", "Torchbox Wagtail"

    logo = models.CharField(choices=Logo.choices, default=Logo.TORCHBOX, max_length=50)

    hero = StreamField([("hero", DynamicHeroBlock())], max_num=1, min_num=1)
    body = StreamField(DivisionStoryBlock(), blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel(
            "logo",
            heading="Division logo",
            help_text=(
                "The logo displayed for this page and any other pages"
                " under this division. (e.g. Charity)"
            ),
        ),
        FieldPanel("hero"),
        FieldPanel("body"),
    ]

    promote_panels = BasePage.promote_panels
