from django.db import models

from modelcluster.fields import ParentalKey
from tbx.core.utils.models import SocialFields
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from .blocks import ServiceStoryBlock


class ServicePageFeaturedBlogPost(Orderable):
    page = ParentalKey(
        "services.ServicePage", on_delete=models.CASCADE, related_name="featured_blogs"
    )

    featured_blog = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [PageChooserPanel("featured_blog", "blog.BlogPage")]


class ServicePageFeaturedWorkPost(Orderable):
    page = ParentalKey(
        "services.ServicePage",
        on_delete=models.CASCADE,
        related_name="featured_work_posts",
    )

    featured_work_post = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [PageChooserPanel("featured_work_post", "work.WorkPage")]


class ServicePage(SocialFields, Page):
    template = "patterns/pages/service/service_page.html"

    intro = RichTextField(blank=True)
    body = StreamField(ServiceStoryBlock(), use_json_field=True)
    featured_blog_heading = models.TextField(blank=True)
    featured_work_post_heading = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("featured_blog_heading", heading="Heading"),
                InlinePanel("featured_blogs", label="Featured Blogs", max_num=3),
            ],
            heading="Featured Blog Post Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("featured_work_post_heading", heading="Heading"),
                InlinePanel(
                    "featured_work_posts", label="Featured Work Posts", max_num=3
                ),
            ],
            heading="Featured Work Post Section",
        ),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]
