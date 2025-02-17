from django.db import models
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.blocks import PageChooserBlock, StreamBlock, StructBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from tbx.core.utils.fields import StreamField
from tbx.core.utils.models import (
    ColourThemeMixin,
    NavigationFields,
    SocialFields,
)
from tbx.people.models import ContactMixin

from .blocks import HomePageStoryBlock, StandardPageStoryBlock


@register_snippet
class EventType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# A couple of abstract classes that contain commonly used fields
class ContentBlock(models.Model):
    content = RichTextField()

    panels = [
        FieldPanel("content"),
    ]

    class Meta:
        abstract = True


class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    link_document = models.ForeignKey(
        "wagtaildocs.Document",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    panels = [
        FieldPanel("link_external"),
        FieldPanel("link_page"),
        FieldPanel("link_document"),
    ]

    class Meta:
        abstract = True

    @property
    def link(self):
        if self.link_page_id:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external


# Carousel items
class CarouselItem(LinkFields):
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("embed_url"),
        FieldPanel("caption"),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Related links
class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel("title"),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class HomePagePartnerLogo(Orderable):
    page = ParentalKey("torchbox.HomePage", related_name="logos")
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("image"),
    ]


# Home Page
class HomePage(ColourThemeMixin, ContactMixin, SocialFields, NavigationFields, Page):
    template = "patterns/pages/home/home_page.html"
    introduction = models.TextField(blank=True)
    body = StreamField(HomePageStoryBlock())

    class Meta:
        verbose_name = "Homepage"

    @cached_property
    def partner_logos(self):
        if logos := self.logos.all().select_related("image"):
            return [logo.image for logo in logos]
        return []

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        InlinePanel("logos", heading="Partner logos", label="logo", max_num=7),
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

    def get_context(self, request):
        context = super().get_context(request)
        context["is_home_page"] = True
        return context


# Standard page
class StandardPage(
    ColourThemeMixin, ContactMixin, SocialFields, NavigationFields, Page
):
    template = "patterns/pages/standard/standard_page.html"

    body = StreamField(StandardPageStoryBlock())

    content_panels = Page.content_panels + [
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

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]


# No longer in use but kept for migration history
class Tag(models.Model):  # noqa: DJ008
    pass


class SubMenuItemBlock(StreamBlock):
    # subitem = PageChooserBlock()
    related_listing_page = PageChooserBlock()


class MenuItemBlock(StructBlock):
    page = PageChooserBlock()
    subitems = SubMenuItemBlock(blank=True, null=True)

    class Meta:
        template = "torchbox/includes/menu_item.html"


class MenuBlock(StreamBlock):
    items = MenuItemBlock()


@register_setting
class MainMenu(BaseSiteSetting):
    menu = StreamField(MenuBlock(), blank=True)

    panels = [
        FieldPanel("menu"),
    ]


@register_setting
class ImportantPageSettings(BaseSiteSetting):
    cookie_policy_page = models.ForeignKey(
        "wagtailcore.Page",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    carbon_emissions_page = models.ForeignKey(
        "wagtailcore.Page",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("cookie_policy_page"),
        FieldPanel("carbon_emissions_page"),
    ]
