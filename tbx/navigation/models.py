from modelcluster.models import ClusterableModel
from tbx.core.blocks import ImageWithLinkBlock
from tbx.navigation.blocks import LinkBlock, PrimaryNavLinkBlock
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField


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
        [("logos", ImageWithLinkBlock())],
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
