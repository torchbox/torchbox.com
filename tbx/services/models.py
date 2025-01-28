from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField
from tbx.core.utils.models import (
    ColourThemeMixin,
    ContactMixin,
    DivisionMixin,
    NavigationFields,
    SocialFields,
)

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


class ServiceAreaPage(DivisionMixin, BasePage):
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

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + NavigationFields.promote_panels
        + ColourThemeMixin.promote_panels
        + DivisionMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]
