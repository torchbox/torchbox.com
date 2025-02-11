from django.contrib.contenttypes.fields import GenericRelation
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.exceptions import ValidationError
from django.db import models

from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import RevisionMixin
from wagtail.snippets.models import register_snippet

from tbx.core.utils.fields import StreamField
from tbx.navigation.blocks import (
    FooterLogoBlock,
    LinkBlock,
    PrimaryNavLinkBlock,
    SecondaryNavMenuBlock,
)


@register_snippet
class NavigationSet(RevisionMixin, models.Model):
    name = models.CharField(max_length=255)
    navigation = StreamField(
        [
            ("link", LinkBlock(icon="link")),
            ("menu", SecondaryNavMenuBlock()),
        ],
    )

    # This will let us do revision.navigation_set
    _revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="navigation_set"
    )

    def __str__(self):
        return self.name

    @property
    def revisions(self):
        return self._revisions


@register_setting(icon="list-ul")
class NavigationSettings(BaseSiteSetting, ClusterableModel):
    primary_navigation = StreamField(
        [("link", PrimaryNavLinkBlock())],
        blank=True,
        help_text="Main site navigation",
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

    panels = [
        FieldPanel("primary_navigation"),
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

        fragment_keys = ["primarynav", "primarynavmobile", "footerlinks"]

        # The fragment cache varies on:
        # the current site pk, whether used in the pattern library

        # NOTE: `is_pattern_library` returns True if pattern is being rendered in the pattern library,
        # but it doesn't return False if otherwise, hence the empty string instead of False
        is_pattern_library_options = [True, ""]

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
