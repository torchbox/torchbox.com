from itertools import chain
import math
import string

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Case, Q, When
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.http import urlencode

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.models import Page
from wagtail.search import index
from wagtail.signals import page_published

from bs4 import BeautifulSoup

from tbx.core.blocks import StoryBlock
from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField
from tbx.core.utils.models import (
    ColourThemeMixin,
    ContactMixin,
    SocialFields,
)
from tbx.images.models import CustomImage
from tbx.taxonomy.models import Sector, Service


class BlogIndexPage(BasePage):
    template = "patterns/pages/blog/blog_listing.html"

    subpage_types = ["BlogPage"]

    @cached_property
    def taxonomy_slugs(self):
        services = Service.objects.values_list("slug", flat=True)
        sectors = Sector.objects.values_list("slug", flat=True)
        return services.union(sectors)

    @property
    def blog_posts(self):
        prefetch_author_images = models.Prefetch(
            "authors__author__image",
            queryset=CustomImage.objects.prefetch_renditions(
                "format-webp|fill-100x100",
                "format-webp|fill-144x144",
                "format-webp|fill-286x286",
            ),
        )
        # Get list of blog pages that are descendants of this page
        blog_posts = (
            BlogPage.objects.live()
            .public()
            .descendant_of(self)
            .distinct()
            .prefetch_related(
                "authors__author",
                "related_sectors",
                "related_services",
                prefetch_author_images,
            )
        )

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

        if slug_filter and slug_filter in self.taxonomy_slugs:
            blog_posts = blog_posts.filter(
                Q(related_sectors__slug=slug_filter)
                | Q(related_services__slug=slug_filter)
            )
            extra_url_params["filter"] = slug_filter

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


class BlogPage(BasePage):
    template = "patterns/pages/blog/blog_detail.html"

    parent_page_types = ["BlogIndexPage"]

    date = models.DateField("Post date")
    body = StreamField(StoryBlock())
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
    search_fields = BasePage.search_fields + [
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

    def get_related_blog_posts(self):
        # Assumption that blog posts for the same division
        # will be under the same blog index page.
        base_queryset = BlogPage.objects.sibling_of(self)
        order_by = ["-date"]

        if related := self.related_posts.values_list("page"):
            # If some blog posts have been manually selected we show those first
            base_queryset |= BlogPage.objects.filter(pk__in=related)
            manual_first = Case(When(pk__in=related, then=1), default=2)
            order_by.insert(0, manual_first)

        prefetch_author_images = models.Prefetch(
            "authors__author__image",
            queryset=CustomImage.objects.prefetch_renditions(
                "format-webp|fill-100x100",
                "format-webp|fill-144x144",
                "format-webp|fill-286x286",
            ),
        )

        return (
            base_queryset.live()
            .public()
            .defer_streamfields()
            .prefetch_related("authors__author", prefetch_author_images)
            .distinct()
            .order_by(*order_by)
            .exclude(pk=self.pk)
        )

    @cached_property
    def related_blog_posts(self):
        return self.get_related_blog_posts()[:3]

    @cached_property
    def blog_index(self):
        ancestor = BlogIndexPage.objects.ancestor_of(self).order_by("-depth").first()

        if ancestor:
            return ancestor
        else:
            # No ancestors are blog indexes,
            # just return first blog index in database
            return BlogIndexPage.objects.first()

    @cached_property
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

    content_panels = BasePage.content_panels + [
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
            InlinePanel(
                "related_posts",
                label="Related posts",
                help_text=(
                    "Related posts are always listed by date (most recent first), "
                    "and will be automatically generated if left blank."
                ),
                max_num=3,
            ),
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )


class RelatedBlogPage(models.Model):
    parent = ParentalKey(
        BlogPage, on_delete=models.CASCADE, related_name="related_posts"
    )
    page = models.ForeignKey(BlogPage, on_delete=models.CASCADE, related_name="+")

    def __str__(self):
        return self.page.title

    panels = [PageChooserPanel("page")]


@receiver(page_published, sender=BlogPage)
def update_body_word_count_on_page_publish(instance, **kwargs):
    instance.set_body_word_count()
    instance.save(update_fields=["body_word_count"])
