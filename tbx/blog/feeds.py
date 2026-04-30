from datetime import datetime, time
from typing import TYPE_CHECKING, Any, Optional

from django.contrib.syndication.views import Feed

import filetype

from .models import BlogPage


if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from wagtail.query import PageQuerySet

# Main blog feed


class BlogFeed(Feed):
    title = "The Torchbox Blog"
    link = "/news/"
    description = "The latest news and views from Torchbox on the work we do, the web and the wider world"
    request: Optional["HttpRequest"] = None

    def __call__(
        self, request: "HttpRequest", *args: Any, **kwargs: Any
    ) -> "HttpResponse":
        self.request = request

        return super().__call__(request, *args, **kwargs)

    def items(self) -> "PageQuerySet[BlogPage]":
        return (
            BlogPage.objects.live()
            .public()
            .defer_streamfields()
            .select_related("feed_image")
            .prefetch_related("authors__author")
            .order_by("-date")[:10]
        )

    def item_title(self, item: BlogPage) -> str:
        return item.title

    def item_description(self, item: BlogPage) -> str:
        return item.listing_summary or item.search_description

    def item_link(self, item: BlogPage) -> str:
        return item.get_full_url(request=self.request)

    def item_author_name(self, item: BlogPage) -> str | None:
        return (
            ", ".join([author_item.author.name for author_item in item.authors.all()])
            or None
        )

    def item_pubdate(self, item: BlogPage) -> datetime:
        return datetime.combine(item.date, time())

    def item_enclosure_url(self, item: BlogPage) -> str | None:
        if item.feed_image:
            return item.feed_image.file.url

    def item_enclosure_mime_type(self, item: BlogPage) -> str | None:
        if item.feed_image:
            try:
                if image_format := filetype.guess_extension(item.feed_image.file):
                    return f"image/{image_format}"
            except (AttributeError, OSError, TypeError):
                pass

        return None

    def item_enclosure_length(self, item: BlogPage) -> str | None:
        if item.feed_image:
            try:
                return str(item.feed_image.file.size)
            except (AttributeError, OSError, TypeError):
                pass

        return None
