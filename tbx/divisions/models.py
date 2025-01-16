from django.db import models

from tbx.core.blocks import DynamicHeroBlock
from tbx.core.utils.fields import StreamField
from tbx.core.utils.models import (
    ColourThemeMixin,
    NavigationFields,
    SocialFields,
)
from tbx.people.models import ContactMixin
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page

from .blocks import DivisionStoryBlock


class DivisionPage(
    ColourThemeMixin, ContactMixin, SocialFields, NavigationFields, Page
):
    template = "patterns/pages/divisions/division_page.html"

    parent_page_types = ["torchbox.HomePage"]

    label = models.CharField(blank=True, max_length=50)

    hero = StreamField([("hero", DynamicHeroBlock())], max_num=1, min_num=1)
    body = StreamField(DivisionStoryBlock(), blank=True)

    content_panels = Page.content_panels + [
        FieldPanel(
            "label",
            heading="Division label",
            help_text=(
                "Label displayed beside the logo for this page and any other pages"
                " under this division. (e.g. Charity)"
            ),
        ),
        FieldPanel("hero"),
        FieldPanel("body"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + NavigationFields.promote_panels
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )
