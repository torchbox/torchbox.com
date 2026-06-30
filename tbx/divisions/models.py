from django.db import models

from wagtail.admin.panels import FieldPanel

from tbx.core.blocks import DynamicHeroBlock
from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField

from .blocks import DivisionStoryBlock


class DivisionPage(BasePage):
    template = "patterns/pages/divisions/division_page.html"

    parent_page_types = ["torchbox.HomePage", "sectors.SectorsIndexPage"]

    class Logo(models.TextChoices):
        TORCHBOX = "logo-torchbox", "Torchbox"
        CHARITY = "logo-charity", "Torchbox Charity"
        PUBLIC = "logo-public", "Torchbox Public"
        WAGTAIL = "logo-wagtail", "Torchbox Wagtail"

    logo = models.CharField(choices=Logo, default=Logo.TORCHBOX, max_length=50)

    hero = StreamField([("hero", DynamicHeroBlock())], max_num=1, min_num=1)
    body = StreamField(DivisionStoryBlock(), blank=True)

    sector = models.ForeignKey(
        "taxonomy.Sector",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="division_pages",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel(
            "sector",
            help_text=(
                "Tag this page with a sector so related blog posts, case "
                "studies and other pages sharing the same sector can be "
                "surfaced alongside it."
            ),
        ),
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
