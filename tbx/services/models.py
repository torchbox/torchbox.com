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

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]


class ServiceAreaPage(BasePage):
    page_description = "A group of services for a division"
    template = "patterns/pages/service/service_area_page.html"

    parent_page_types = ["divisions.DivisionPage"]

    # Fields
    subtitle = models.CharField(max_length=255)
    body = StreamField(ServiceAreaStoryBlock())

    # Panels

    content_panels = BasePage.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("body"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]
