from typing import Any
lazy from http import HTTPStatus

from django.db import models
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
lazy from django.http import HttpRequest, HttpResponse

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet
lazy from wagtail.admin.rich_text.converters.html_markdown import (
    HTMLToMarkdownConverter,
)

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
    SocialFields,
)

from .blocks import HomePageStoryBlock, StandardPageStoryBlock


@register_snippet
class EventType(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="Used as the value in event-filter URLs. "
        "Changing it will break existing filter links.",
    )

    panels = [
        "name",
        "slug",
    ]

    def __str__(self):
        return self.name


# A couple of abstract classes that contain commonly used fields
class ContentBlock(models.Model):
    content = RichTextField()

    panels = ["content"]

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

    panels = ["link_external", "link_page", "link_document"]

    class Meta:
        abstract = True

    @property
    def link(self):
        if self.link_page_id:
            # FIXME: find a way to pass request to use .get_url(request)
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
        "image",
        "embed_url",
        "caption",
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Related links
class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        "title",
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class BasePage(
    ColourThemeMixin,
    ContactMixin,
    DivisionMixin,
    NavigationFields,
    SocialFields,
    Page,
):
    class Meta:
        abstract = True

    response_media_types = ["text/html", "text/markdown"]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        *NavigationFields.promote_panels,
        *ColourThemeMixin.promote_panels,
        *DivisionMixin.promote_panels,
        *ContactMixin.promote_panels,
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]

    @cached_property
    def breadcrumbs(self):
        """
        Return the current page's ancestors starting at the homepage.
        """
        # The homepage has depth=2; anything shallower is the Wagtail root.
        return self.get_ancestors().filter(depth__gte=2)

    def get_response_media_type(self, request: HttpRequest):
        # Demo only: ?format=md shows the Markdown in a browser, which can't
        # easily send an Accept: text/markdown header.
        if request.GET.get("format") == "md":
            return "text/markdown"
        return super().get_response_media_type(request)

    def serve(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().serve(request, *args, **kwargs)
        # Page responses are TemplateResponses, rendered lazily.
        if hasattr(response, "render"):
            response.render()
        # Leave redirects, errors and non-HTML responses as they are.
        if response.status_code != HTTPStatus.OK or "text/html" not in response.get(
            "Content-Type", ""
        ):
            return response

        if self.get_response_media_type(request) != "text/markdown":
            # add the Link header and return
            response["Link"] = (
                f'{self.get_url(request)}?format=md; rel="alternate"; type="text/markdown"'
            )
            return response

        # Finally, convert to Markdown
        converter = HTMLToMarkdownConverter(base_url=self.get_full_url(request))
        markdown = converter.convert(response.content.decode(response.charset))
        response = HttpResponse(markdown, content_type="text/markdown; charset=utf-8")

        # Rough token count for the `x-markdown-tokens` header, using the common ~4 characters per token heuristic.
        # Agents only use it to budget context, so an estimate avoids pulling in a tokenizer.
        response["x-markdown-tokens"] = max(1, round(len(markdown) / 4))

        return response


class HomePagePartnerLogo(Orderable):
    page = ParentalKey("torchbox.HomePage", related_name="logos")
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = ["image"]


# Home Page
class HomePage(
    ColourThemeMixin,
    ContactMixin,
    NavigationFields,
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
        "body",
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        *NavigationFields.promote_panels,
        *ColourThemeMixin.promote_panels,
        *ContactMixin.promote_panels,
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
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

    content_panels = [
        *BasePage.content_panels,
        "body",
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]


# No longer in use but kept for migration history
class Tag(models.Model):  # noqa: DJ008
    pass


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
        "cookie_policy_page",
        "carbon_emissions_page",
    ]
