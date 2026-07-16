from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index

from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField

from .blocks import ServiceAreaStoryBlock, ServiceStoryBlock


class ServicePage(BasePage):
    template = "patterns/pages/service/service_page.html"

    intro = RichTextField(blank=True)
    body = StreamField(ServiceStoryBlock())
    service = models.ForeignKey(
        "taxonomy.Service",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_pages",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel(
            "service",
            help_text=(
                "Tag this page with a service so related blog posts, case "
                "studies and other pages sharing the same service can be "
                "surfaced alongside it."
            ),
        ),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    subpage_types = [
        "services.ServicePage",
        "services.ServiceAreaPage",
        "divisions.DivisionPage",
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]


class ServiceAreaPage(BasePage):
    page_description = "A group of services for a division"
    template = "patterns/pages/service/service_area_page.html"

    parent_page_types = [
        "divisions.DivisionPage",
        "sectors.SectorsIndexPage",
        "services.ServicePage",
    ]
    subpage_types = ["services.ServicePage"]

    # Fields
    subtitle = models.CharField(max_length=255)
    body = StreamField(ServiceAreaStoryBlock())
    sector = models.ForeignKey(
        "taxonomy.Sector",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_area_pages",
    )

    # Panels

    content_panels = BasePage.content_panels + [
        FieldPanel(
            "sector",
            help_text=(
                "Tag this page with a sector so related blog posts, case "
                "studies and other pages sharing the same sector can be "
                "surfaced alongside it."
            ),
        ),
        FieldPanel("subtitle"),
        FieldPanel("body"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]
