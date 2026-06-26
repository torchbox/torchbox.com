from django.dispatch import receiver

from wagtail.signals import page_published, page_unpublished


@receiver(page_published)
@receiver(page_unpublished)
def invalidate_primary_nav_on_page_change(sender, instance, **kwargs):
    """
    Drop the cached primary navigation for the page's site when it's
    published or unpublished — link titles, URLs, children and the
    auto-resolved lists (divisions, taxonomy, page_children) can all
    shift, so we invalidate rather than try to track dependencies.
    """
    from tbx.navigation.utils import invalidate_primary_nav_cache

    site = instance.get_site()
    if site is None:
        return
    invalidate_primary_nav_cache(site)
