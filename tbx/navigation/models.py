from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from modelcluster.models import ClusterableModel
from tbx.core.utils.fields import StreamField
from tbx.navigation.blocks import (
    FooterLogoBlock,
    LinkBlock,
    PrimaryNavLinkBlock,
)
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


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

    panels = [
        FieldPanel("primary_navigation"),
        FieldPanel("footer_links"),
        FieldPanel("footer_logos"),
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
