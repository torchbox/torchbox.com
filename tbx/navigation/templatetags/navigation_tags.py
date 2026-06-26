from django import template

from wagtail.models import Site

from tbx.navigation.utils import (
    get_primary_navigation,
    is_current_nav_item,
)
from tbx.people.models import Contact
from tbx.sitemap.models import SitemapPage


register = template.Library()


def _navigation_settings(context):
    return context["settings"]["navigation"]["NavigationSettings"]


def _build_primary_nav_context(context):
    request = context["request"]
    current_page = context.get("page")
    site = (
        Site.find_for_request(request)
        or Site.objects.filter(is_default_site=True).first()
    )

    # Memoise on the request so desktop + mobile inclusion tags share one
    # lookup. Keyed on site.pk so a request resolving to a different site
    # between calls (e.g. preview switching) doesn't reuse a stale list.
    memo = getattr(request, "_primary_navigation", None)
    if memo is None or memo[0] != site.pk:
        resolved_items = get_primary_navigation(site)
        request._primary_navigation = (site.pk, resolved_items)
    else:
        resolved_items = memo[1]

    # request.path is the canonical current URL — Django guarantees it on
    # any real request, and it avoids re-resolving via Page.get_url() per
    # nav item. Empty string is harmless: is_current_nav_item short-circuits.
    current_url = getattr(request, "path", "")

    return {
        "nav_items": [
            {
                "item": item,
                "is_current": is_current_nav_item(item, current_page, current_url),
            }
            for item in resolved_items
        ],
        "request": request,
    }


def _build_header_actions_context(context):
    request = context["request"]
    nav_settings = _navigation_settings(context)

    header_cta_url = ""
    header_cta_text = nav_settings.header_cta_text or "Get in touch"
    if nav_settings.header_cta_page:
        header_cta_url = nav_settings.header_cta_page.url
    elif default_contact := Contact.objects.filter(default_contact=True).first():
        header_cta_url = default_contact.link
        if not nav_settings.header_cta_text:
            header_cta_text = default_contact.button_text

    return {
        "header_cta_url": header_cta_url,
        "header_cta_text": header_cta_text,
        "request": request,
    }


# Primary nav desktop snippet
@register.inclusion_tag(
    "patterns/navigation/components/primary-nav.html", takes_context=True
)
def primarynav(context):
    return _build_primary_nav_context(context)


# Primary nav mobile snippets
@register.inclusion_tag(
    "patterns/navigation/components/primary-nav-mobile.html", takes_context=True
)
def primarynavmobile(context):
    return _build_primary_nav_context(context)


@register.inclusion_tag(
    "patterns/navigation/components/header-actions.html", takes_context=True
)
def headeractions(context):
    return _build_header_actions_context(context)


# Footer nav snippets
@register.inclusion_tag(
    "patterns/navigation/components/footer-links.html", takes_context=True
)
def footerlinks(context):
    request = context["request"]
    return {
        "footerlinks": context["settings"]["navigation"][
            "NavigationSettings"
        ].footer_links,
        "sitemap_page": SitemapPage.objects.live().first(),
        "request": request,
    }
