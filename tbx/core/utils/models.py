from django.db import models
from django.utils.translation import gettext as _

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable

SEARCH_DESCRIPTION_LABEL = "Meta description"  # NOTE changing this requires migrations


class PageAuthor(Orderable):
    page = ParentalKey("wagtailcore.Page", related_name="authors")
    author = models.ForeignKey(
        "people.Author", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("author"),
    ]


# Generic social fields abstract class to add social image/text to any new content type easily.
class SocialFields(models.Model):
    social_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    social_text = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [FieldPanel("social_image"), FieldPanel("social_text")],
        )
    ]


@register_setting
class SocialMediaSettings(BaseSiteSetting):
    twitter_handle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Your Twitter username without the @, e.g. katyperry",
    )
    facebook_app_id = models.CharField(
        max_length=255, blank=True, help_text="Your Facebook app ID."
    )
    default_sharing_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Default sharing text to use if social text has not been set on a page.",
    )
    site_name = models.CharField(
        max_length=255,
        blank=True,
        default="{{ cookiecutter.project_name }}",
        help_text="Site name, used by Open Graph.",
    )


class ColourTheme(models.TextChoices):
    NONE = "", "None"
    CORAL = "theme-coral", "Coral"
    LAGOON = "theme-lagoon", "Lagoon"
    BANANA = "theme-banana", "Banana"


class ColourThemeMixin(models.Model):
    """
    Provides a `theme` field to allow pages to be styled with a colour theme.
    """

    theme = models.CharField(
        max_length=25,
        blank=True,
        choices=ColourTheme.choices,
        help_text=_(
            "The theme will be applied to this page and all of it's "
            "descendants. If no theme is selected, it will be derived from "
            "this page's ancestors."
        ),
    )

    @property
    def theme_class(self):
        if theme := self.theme:
            return theme
        if parent := self.get_parent():
            specific_parent = parent.get_specific(deferred=True)
            if not parent.is_root() and hasattr(specific_parent, "theme"):
                return specific_parent.theme_class
        return ColourTheme.NONE

    content_panels = [FieldPanel("theme")]

    class Meta:
        abstract = True
