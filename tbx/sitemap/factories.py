import wagtail_factories

from tbx.sitemap.models import SitemapPage


class SitemapPageFactory(wagtail_factories.PageFactory):
    title = "Sitemap"

    class Meta:
        model = SitemapPage
