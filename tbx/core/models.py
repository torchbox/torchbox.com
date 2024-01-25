from django.db import models

from modelcluster.fields import ParentalKey
from tbx.core.utils.models import SocialFields
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.blocks import PageChooserBlock, StreamBlock, StructBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from .blocks import ServiceStoryBlock, StoryBlock


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

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel("link_external"),
        FieldPanel("link_page"),
        FieldPanel("link_document"),
    ]

    class Meta:
        abstract = True


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


# Home Page
class HomePageFeaturedPost(Orderable):
    page = ParentalKey(
        "torchbox.HomePage", on_delete=models.CASCADE, related_name="featured_posts"
    )
    featured_post = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        PageChooserPanel("featured_post", ["blog.BlogPage", "work.HistoricalWorkPage"]),
    ]


class HomePageHeroImage(Orderable):
    page = ParentalKey(
        "torchbox.HomePage", on_delete=models.CASCADE, related_name="hero_images"
    )
    image = models.ForeignKey(
        "images.CustomImage",
        help_text="The hero images will be displayed in a random order.",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name="+",
    )


class HomePage(SocialFields, Page):
    template = "patterns/pages/home/home_page.html"
    hero_intro_primary = models.TextField(blank=True)
    hero_intro_secondary = models.TextField(blank=True)
    intro_body = RichTextField(blank=True)
    work_title = models.TextField(blank=True)
    blog_title = models.TextField(blank=True)
    clients_title = models.TextField(blank=True)

    class Meta:
        verbose_name = "Homepage"

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_intro_primary"),
                FieldPanel("hero_intro_secondary"),
                InlinePanel("hero_images", label="Hero Images", max_num=6, min_num=1),
            ],
            heading="Hero intro",
        ),
        InlinePanel("featured_posts", label="Featured Posts", max_num=3),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context.update(
            hero_images=self.hero_images.all(),
        )
        return context

    @property
    def blog_posts(self):
        from tbx.blog.models import BlogPage

        # Get list of blog pages.
        blog_posts = BlogPage.objects.live().public()

        # Order by most recent date first
        blog_posts = blog_posts.order_by("-date")

        return blog_posts


# Standard page


class StandardPage(SocialFields, Page):
    template = "patterns/pages/standard/standard_page.html"

    body = StreamField(StoryBlock(), use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]


# Currently hidden. These were used in the past and may be used again in the future
# @register_snippet
class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BaseAddress(blocks.StructBlock):
    title = blocks.CharBlock(blank=True)
    address = blocks.RichTextBlock(blank=True)


@register_setting
class GlobalSettings(BaseSiteSetting):
    addresses = StreamField(
        [("address", BaseAddress())], blank=True, use_json_field=True
    )

    panels = [
        FieldPanel("addresses"),
    ]

    class Meta:
        verbose_name = "Global Settings"


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
    menu = StreamField(MenuBlock(), blank=True, use_json_field=True)

    panels = [
        FieldPanel("menu"),
    ]


class ServicePage(SocialFields, Page):
    template = "patterns/pages/service/service_page.html"

    intro = RichTextField(blank=True)
    body = StreamField(ServiceStoryBlock(), use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]
