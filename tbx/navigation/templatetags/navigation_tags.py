from django import template

from tbx.navigation.utils import (
    item_has_dropdown,
    primary_nav_item_is_current,
    resolve_primary_nav_dropdown,
)
from tbx.people.models import Contact
from tbx.sitemap.models import SitemapPage


register = template.Library()


def _navigation_settings(context):
    return context["settings"]["navigation"]["NavigationSettings"]


def _build_primary_nav_context(context):
    request = context["request"]
    nav_settings = _navigation_settings(context)
    current_page = context.get("page")

    items = []
    for block in nav_settings.primary_navigation:
        link = block.value
        dropdown = (
            resolve_primary_nav_dropdown(link) if item_has_dropdown(link) else None
        )
        items.append(
            {
                "link": link,
                "dropdown": dropdown,
                "is_current": primary_nav_item_is_current(link, current_page),
            }
        )

    header_cta_url = ""
    header_cta_text = nav_settings.header_cta_text or "Get in touch"
    if nav_settings.header_cta_page:
        header_cta_url = nav_settings.header_cta_page.url
    elif default_contact := Contact.objects.filter(default_contact=True).first():
        header_cta_url = default_contact.link
        if not nav_settings.header_cta_text:
            header_cta_text = default_contact.button_text

    return {
        "nav_items": items,
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
    return _build_primary_nav_context(context)


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
