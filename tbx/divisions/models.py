from django.core.exceptions import ValidationError
from django.db import models

from wagtail.admin.panels import FieldPanel

from tbx.core.blocks import DynamicHeroBlock
from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField

from .blocks import DivisionStoryBlock


class DivisionPage(BasePage):
    template = "patterns/pages/divisions/division_page.html"

    parent_page_types = [
        "torchbox.HomePage",
        "sectors.SectorsIndexPage",
        "services.ServicePage",
    ]

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
    service = models.ForeignKey(
        "taxonomy.Service",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="division_pages",
    )

    def clean(self):
        super().clean()
        if self.sector_id and self.service_id:
            raise ValidationError(
                "A division page can be tagged with a sector or a service, not both."
            )

    content_panels = BasePage.content_panels + [
        FieldPanel(
            "sector",
            help_text=(
                "Tag this page with a sector so related blog posts, case "
                "studies and other pages sharing the same sector can be "
                "surfaced alongside it. Cannot be set alongside a service."
            ),
        ),
        FieldPanel(
            "service",
            help_text=(
                "Tag this page with a service so related blog posts, case "
                "studies and other pages sharing the same service can be "
                "surfaced alongside it. Cannot be set alongside a sector."
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
