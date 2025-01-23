import logging

from django.core.management.base import BaseCommand

from wagtail.embeds.embeds import get_embed
from wagtail.embeds.exceptions import EmbedException
from wagtail.embeds.models import Embed


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Updates existing YouTube embeds in the database, so that they
    use `lite_youtube_embed.LiteYouTubeEmbedFinder` instead of
    `wagtail.embeds.finders.oembed`.
    """

    def handle(self, *args, **options):
        youtube_embeds = Embed.objects.filter(provider_name="YouTube")
        urls = list(youtube_embeds.values_list("url", flat=True))

        # delete the embeds
        youtube_embeds.delete()

        # re-create them
        for index, url in enumerate(urls, start=1):
            try:
                get_embed(url)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{index}/{len(urls)}. Successfully created embed for {url}"
                    )
                )
            except EmbedException as e:
                logger.exception(
                    "Error occured while attempting to create an embed for %s:\n%s",
                    url,
                    e,
                )
