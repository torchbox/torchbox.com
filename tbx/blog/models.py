import math
import string
from itertools import chain

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.http import urlencode

from bs4 import BeautifulSoup
from modelcluster.fields import ParentalManyToManyField
from tbx.core.blocks import StoryBlock
from tbx.core.utils.models import ColourThemeMixin, SocialFields
from tbx.people.models import ContactMixin
from tbx.taxonomy.models import Sector, Service
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.signals import page_published


class BlogIndexPage(ColourThemeMixin, ContactMixin, SocialFields, Page):
    template = "patterns/pages/blog/blog_listing.html"

    subpage_types = ["BlogPage"]

    @property
    def blog_posts(self):
        # Get list of blog pages that are descendants of this page
        blog_posts = BlogPage.objects.live().descendant_of(self).distinct()

        # Order by most recent date first
        blog_posts = blog_posts.order_by("-date", "pk")

        return blog_posts

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get blog_posts
        blog_posts = self.blog_posts

        # Filter by related_service slug
        slug_filter = request.GET.get("filter")
        extra_url_params = {}

        if slug_filter:
            blog_posts = blog_posts.filter(
                Q(related_sectors__slug=slug_filter)
                | Q(related_services__slug=slug_filter)
            )
            extra_url_params["filter"] = slug_filter

        # format for template
        blog_posts = [
            {
                "title": blog_post.title,
                "url": blog_post.url,
                "author": blog_post.first_author,
                "date": blog_post.date,
                "read_time": blog_post.read_time,
                "type": blog_post.type,
                "tags": blog_post.tags,
            }
            for blog_post in blog_posts
        ]

        # use page to filter
        page = request.GET.get("page", 1)

        # Pagination
        paginator = Paginator(blog_posts, 10)  # Show 10 blog_posts per page

        try:
            blog_posts = paginator.page(page)
        except PageNotAnInteger:
            blog_posts = paginator.page(1)
        except EmptyPage:
            blog_posts = paginator.page(paginator.num_pages)

        # Only show Sectors and Services that have been used
        related_sectors = Sector.objects.filter(
            pk__in=models.Subquery(self.blog_posts.values("related_sectors"))
        )

        related_services = Service.objects.filter(
            pk__in=models.Subquery(self.blog_posts.values("related_services"))
        )
        tags = chain(related_services, related_sectors)

        context.update(
            blog_posts=blog_posts,
            tags=tags,
            extra_url_params=urlencode(extra_url_params),
        )
        return context

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )


class BlogPage(ColourThemeMixin, ContactMixin, SocialFields, Page):
    template = "patterns/pages/blog/blog_detail.html"

    parent_page_types = ["BlogIndexPage"]

    date = models.DateField("Post date")
    body = StreamField(StoryBlock(), use_json_field=True)
    body_word_count = models.PositiveIntegerField(null=True, editable=False)

    feed_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    listing_summary = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True, max_length=255)
    related_sectors = ParentalManyToManyField(
        "taxonomy.Sector",
        related_name="blog_posts",
        blank=True,
    )
    related_services = ParentalManyToManyField(
        "taxonomy.Service", related_name="blog_posts"
    )
    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    def set_body_word_count(self):
        body_basic_html = self.body.stream_block.render_basic(self.body)
        body_text = BeautifulSoup(body_basic_html, "html.parser").get_text()
        remove_chars = string.punctuation + "“”’"
        body_words = body_text.translate(
            body_text.maketrans(dict.fromkeys(remove_chars))
        ).split()
        self.body_word_count = len(body_words)

    @cached_property
    def sectors(self):
        return self.related_sectors.all()

    @cached_property
    def services(self):
        return self.related_services.all()

    @property
    def tags(self):
        return chain(self.services, self.sectors)

    @property
    def related_blog_posts(self):
        # format for template
        return [
            {
                "title": blog_post.title,
                "url": blog_post.url,
                "author": blog_post.first_author,
                "date": blog_post.date,
                "read_time": blog_post.read_time,
                "type": blog_post.type,
                "tags": self.tags,
            }
            for blog_post in BlogPage.objects.filter(
                Q(related_sectors__in=self.sectors)
                | Q(related_services__in=self.services)
            )
            .live()
            .prefetch_related("related_sectors", "related_services")
            .defer_streamfields()
            .distinct()
            .order_by("-first_published_at")
            .exclude(pk=self.pk)[:3]
        ]

    @cached_property
    def blog_index(self):
        ancestor = BlogIndexPage.objects.ancestor_of(self).order_by("-depth").first()

        if ancestor:
            return ancestor
        else:
            # No ancestors are blog indexes,
            # just return first blog index in database
            return BlogIndexPage.objects.first()

    @property
    def first_author(self):
        """Safely return the first author if one exists."""
        author = self.authors.first()
        if author:
            return author.author
        return None

    @property
    def read_time(self):
        if self.body_word_count:
            return math.ceil(self.body_word_count / 275)
        else:
            return "x"

    @property
    def type(self):
        return "BLOG POST"

    content_panels = Page.content_panels + [
        InlinePanel("authors", label="Author", min_num=1),
        FieldPanel("date"),
        FieldPanel("body"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            FieldPanel("feed_image"),
            FieldPanel("listing_summary"),
            FieldPanel("canonical_url"),
            MultiFieldPanel(
                [
                    FieldPanel("related_sectors", widget=forms.CheckboxSelectMultiple),
                    FieldPanel("related_services", widget=forms.CheckboxSelectMultiple),
                ],
                heading="Taxonomies",
            ),
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )


@receiver(page_published, sender=BlogPage)
def update_body_word_count_on_page_publish(instance, **kwargs):
    instance.set_body_word_count()
    instance.save(update_fields=["body_word_count"])
