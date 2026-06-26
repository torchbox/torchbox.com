from django.db.models.signals import post_delete
from django.dispatch import receiver

from wagtail.models import Page
from wagtail.signals import (
    page_published,
    page_slug_changed,
    page_unpublished,
    post_page_move,
)


def _invalidate(site):
    # Local import: signals is loaded at app-ready, before utils' transitive
    # imports are guaranteed to be ready.
    from tbx.navigation.utils import invalidate_primary_nav_cache

    if site is None:
        return
    invalidate_primary_nav_cache(site)


@receiver(page_published)
@receiver(page_unpublished)
@receiver(page_slug_changed)
@receiver(post_page_move)
def invalidate_primary_nav_on_page_change(sender, instance, **kwargs):
    """
    Drop the cached primary navigation when a page changes in a way that
    can affect nav output — publish/unpublish (link target visibility),
    slug change (URL drift), and move (URL drift + page_children lists).

    We invalidate the whole nav rather than try to track which pages it
    references; the cache is rebuilt lazily on the next request.
    """
    _invalidate(instance.get_site())


@receiver(post_delete, sender=Page)
def invalidate_primary_nav_on_page_delete(sender, instance, **kwargs):
    """
    Deleting a page can remove a link target or shrink an auto-resolved
    list (divisions, page_children). get_site() may still resolve via the
    parent's tree path; if not, fall back to invalidating every site.
    """
    site = None
    try:
        site = instance.get_site()
    except Exception:
        site = None

    if site is not None:
        _invalidate(site)
        return

    # Fallback: page is gone so site lookup may fail — clear all sites.
    from wagtail.models import Site

    for site in Site.objects.all():
        _invalidate(site)
