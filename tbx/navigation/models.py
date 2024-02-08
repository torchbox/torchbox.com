from itertools import product

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from modelcluster.models import ClusterableModel
from tbx.navigation.blocks import LinkBlock, PrimaryNavLinkBlock
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock


@register_setting(icon="list-ul")
class NavigationSettings(BaseSiteSetting, ClusterableModel):
    primary_navigation = StreamField(
        [("link", PrimaryNavLinkBlock())],
        blank=True,
        help_text="Main site navigation",
        use_json_field=True,
    )
    footer_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Single list of elements at the base of the page.",
        use_json_field=True,
    )
    footer_logos = StreamField(
        [("logos", blocks.ListBlock(ImageChooserBlock()))],
        blank=True,
        help_text="Single list of logos that appear before the footer box",
        use_json_field=True,
        max_num=4,
    )

    panels = [
        FieldPanel("primary_navigation"),
        FieldPanel("footer_links"),
        FieldPanel("footer_logos"),
    ]

    def save(self, **kwargs):
        super().save(**kwargs)

        fragment_keys = ["primarynav"]

        # The fragment cache varies on:
        # the current site pk, whether used in preview, or in the pattern library

        request_is_preview_options = [True, False]
        # NOTE: `is_pattern_library` returns True if pattern is being rendered in the pattern library,
        # but it doesn't return False if otherwise, hence the empty string instead of False
        is_pattern_library_options = [True, ""]

        # Generate all combinations of `request_is_preview` and `is_pattern_library`
        combinations = product(request_is_preview_options, is_pattern_library_options)

        keys = [
            make_template_fragment_key(key, vary_on=(self.site.pk,) + combination)
            for key in fragment_keys
            for combination in combinations
        ]
        cache.delete_many(keys)
