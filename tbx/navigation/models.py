from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.exceptions import ValidationError
from django.db import models

from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from tbx.core.utils.fields import StreamField
from tbx.navigation.blocks import (
    FooterLogoBlock,
    LinkBlock,
    PrimaryNavLinkBlock,
)


@register_setting(icon="list-ul")
class NavigationSettings(BaseSiteSetting, ClusterableModel):
    primary_navigation = StreamField(
        [("link", PrimaryNavLinkBlock())],
        blank=True,
        help_text=(
            "Main site navigation. See docs/navigation.md for IA mapping, "
            "dropdown styles, content sources, and per-item configuration."
        ),
    )
    footer_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Single list of elements at the base of the page.",
    )
    footer_logos = StreamField(
        [("logo", FooterLogoBlock())],
        blank=True,
        help_text="Single list of logos that appear before the footer box",
    )
    footer_newsletter_cta_url = models.URLField(blank=True)
    footer_newsletter_cta_text = models.CharField(blank=True, max_length=255)
    header_cta_page = models.ForeignKey(
        "wagtailcore.Page",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Page linked from the header “Get in touch” button.",
    )
    header_cta_text = models.CharField(
        blank=True,
        max_length=255,
        default="Get in touch",
        help_text="Text for the header “Get in touch” button.",
    )

    panels = [
        FieldPanel("primary_navigation"),
        MultiFieldPanel(
            [
                FieldPanel("header_cta_page"),
                FieldPanel("header_cta_text"),
            ],
            heading="Header actions",
        ),
        FieldPanel("footer_links"),
        FieldPanel("footer_logos"),
        MultiFieldPanel(
            [
                FieldPanel("footer_newsletter_cta_url", heading="External link"),
                FieldPanel("footer_newsletter_cta_text", heading="Text"),
            ],
            heading="Footer newsletter CTA",
        ),
    ]

    def save(self, **kwargs):
        super().save(**kwargs)

        fragment_keys = [
            "footerlinks",
            "headeractions",
        ]

        # The fragment cache varies on:
        # the current site pk, whether used in the pattern library

        # NOTE: `is_pattern_library` is True in the pattern library and otherwise
        # absent from context (resolved as an empty string in the cache tag).
        is_pattern_library_options = [True, "", False]

        keys = [
            make_template_fragment_key(key, vary_on=(self.site.pk, is_pattern_library))
            for is_pattern_library in is_pattern_library_options
            for key in fragment_keys
        ]
        cache.delete_many(keys)

    def clean(self):
        super().clean()

        if self.footer_newsletter_cta_url and not self.footer_newsletter_cta_text:
            msg = "The CTA footer text is required when a URL is supplied"
            raise ValidationError({"footer_newsletter_cta_text": msg})
