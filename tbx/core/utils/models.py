from django.db import models
from django.utils.functional import cached_property
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


class NavigationFields(models.Model):
    navigation_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="""
            Text entered here will appear instead of the page title in the navigation menu.
            For top-level menu items do this in the navigaiton settings instead.
            """,
    )

    class Meta:
        abstract = True

    promote_panels = [
        FieldPanel("navigation_text"),
    ]

    @cached_property
    def nav_text(self):
        return self.navigation_text or self.title


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
        default="Torchbox",
        help_text="Site name, used by Open Graph.",
    )


class ColourTheme(models.TextChoices):
    NONE = "", "None"
    CORAL = "theme-coral", "Coral"
    NEBULINE = "theme-nebuline", "Nebuline"
    LAGOON = "theme-lagoon", "Lagoon"
    GREEN = "theme-green", "Green"


class ColourThemeMixin(models.Model):
    """
    Provides a `theme` field to allow pages to be styled with a colour theme.
    """

    theme = models.CharField(
        max_length=25,
        blank=True,
        choices=ColourTheme.choices,
    )

    @property
    def theme_class(self):
        if theme := self.theme:
            return theme

        try:
            return next(
                p.theme
                for p in self.get_ancestors().specific().order_by("-depth")
                if getattr(p, "theme", ColourTheme.NONE) != ColourTheme.NONE
            )
        except StopIteration:
            return ColourTheme.NONE

    promote_panels = [
        FieldPanel(
            "theme",
            help_text=_(
                "The theme will be applied to this page and all of its descendants. "
                "If no theme is selected, it will be derived from "
                "this page's ancestors."
            ),
        ),
    ]

    class Meta:
        abstract = True


class DivisionMixin(models.Model):
    """
    Provides a 'division' field to allow pages to be associated to a Division.
    """

    division = models.ForeignKey(
        "divisions.DivisionPage",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    @cached_property
    def final_division(self):
        """
        Returns a DivisionPage.

        If a division field is set on the current page, use that.
        If not, check the ancestors.

        The closest ancestor that fulfills one of the following will be followed:
        - the division field is populated, OR
        - the ancestor page is a DivisionPage.
        """
        from tbx.divisions.models import DivisionPage

        if self.division:
            return self.division

        try:
            return next(
                getattr(p, "division", None) or p
                for p in self.get_ancestors()
                .filter(depth__gt=2)
                .specific()
                .defer_streamfields()
                .order_by("-depth")
                if isinstance(getattr(p, "division", None) or p, DivisionPage)
            )
        except StopIteration:
            pass

    promote_panels = [
        FieldPanel(
            "division",
            help_text=_(
                "The division will be applied to this page and its descendants. "
                "If no division is selected, it will be derived from "
                "this page's ancestors. "
                "If one of the ancestors is a division page, that will be used."
            ),
        ),
    ]

    class Meta:
        abstract = True
