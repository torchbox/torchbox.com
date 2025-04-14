from django.db import models
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.blocks import PageChooserBlock, StreamBlock, StructBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from tbx.core.utils.fields import StreamField
from tbx.core.utils.formatting import (
    convert_bold_links_to_pink,
    convert_italic_links_to_purple,
)
from tbx.core.utils.models import (
    ColourThemeMixin,
    ContactMixin,
    DivisionMixin,
    NavigationFields,
    NavigationSetMixin,
    SocialFields,
)

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


class BasePage(
    ColourThemeMixin,
    ContactMixin,
    DivisionMixin,
    NavigationFields,
    NavigationSetMixin,
    SocialFields,
    Page,
):
    class Meta:
        abstract = True

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + NavigationFields.promote_panels
        + NavigationSetMixin.promote_panels
        + ColourThemeMixin.promote_panels
        + DivisionMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )

    @cached_property
    def breadcrumbs(self):
        """
        Return a a list of the current page's ancestors where the first one is
        either a division page, or the homepage if no ancestor is a division page.
        """
        # The homepage has depth=2
        min_depth = 2 if self.final_division is None else self.final_division.depth
        return self.get_ancestors().filter(depth__gte=min_depth)


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
class HomePage(
    ColourThemeMixin,
    ContactMixin,
    NavigationFields,
    NavigationSetMixin,
    SocialFields,
    Page,
):
    template = "patterns/pages/home/home_page.html"

    parent_page_types = ["wagtailcore.Page"]

    hero_heading_1 = models.CharField(max_length=255)
    hero_heading_2 = models.CharField(max_length=255)
    hero_introduction = RichTextField(blank=True, features=["bold", "italic", "link"])
    body = StreamField(HomePageStoryBlock())

    class Meta:
        verbose_name = "Homepage"

    @cached_property
    def partner_logos(self):
        if logos := self.logos.all().select_related("image"):
            return [logo.image for logo in logos]
        return []

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(
                    "hero_heading_1",
                    heading="Heading (Part 1)",
                    help_text="This is the non-bold part of the heading.",
                ),
                FieldPanel(
                    "hero_heading_2",
                    heading="Heading (Part 2)",
                    help_text="This is the bold part of the heading.",
                ),
                FieldPanel(
                    "hero_introduction",
                    heading="Introduction",
                    # mark_safe needed so the HTML tags aren't escaped
                    help_text=mark_safe(
                        "Use bold to mark links as"
                        ' <span style="color:#EE5276">pink</span>,'
                        " and use italics to mark links as"
                        ' <span style="color:#6F60D0">purple</span> '
                        "(the colours will only take effect on larger screen sizes)."
                    ),
                ),
            ],
            heading="Hero",
            help_text=(
                "When combined, part 1 & part 2 of the heading can be treated as one"
                " sentence or one paragraph, depending on the presence of punctuation."
            ),
        ),
        InlinePanel("logos", heading="Partner logos", label="logo", max_num=12),
        FieldPanel("body"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + NavigationFields.promote_panels
        + NavigationSetMixin.promote_panels
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )

    def get_context(self, request):
        context = super().get_context(request)
        context["is_home_page"] = True
        context["hero_introduction"] = convert_bold_links_to_pink(
            convert_italic_links_to_purple(self.hero_introduction)
        )
        return context


# Standard page
class StandardPage(BasePage):
    template = "patterns/pages/standard/standard_page.html"

    body = StreamField(StandardPageStoryBlock())

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    search_fields = BasePage.search_fields + [
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
