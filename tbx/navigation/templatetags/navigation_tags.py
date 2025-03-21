from django import template


register = template.Library()


# Primary nav desktop snippet
@register.inclusion_tag(
    "patterns/navigation/components/primary-nav.html", takes_context=True
)
def primarynav(context):
    request = context["request"]
    return {
        "primarynav": context["settings"]["navigation"][
            "NavigationSettings"
        ].primary_navigation,
        "request": request,
    }


# Primary nav mobile snippets
@register.inclusion_tag(
    "patterns/navigation/components/primary-nav-mobile.html", takes_context=True
)
def primarynavmobile(context):
    request = context["request"]
    return {
        "primarynav": context["settings"]["navigation"][
            "NavigationSettings"
        ].primary_navigation,
        "request": request,
    }


@register.simple_tag(name="get_top_level_parent_page", takes_context=True)
def get_top_level_parent_page(context):
    # Get all page links from the primary nav.
    primary_nav = [
        block.value["page"]
        for block in context["settings"]["navigation"][
            "NavigationSettings"
        ].primary_navigation
        if block.value.get("page", False)
    ]
    # Get all ancestors for this page (highest depth first). Ignores the homepage.
    ancestors = (
        context["page"]
        .get_ancestors(inclusive=True)
        .filter(depth__gte=3)
        .order_by("-depth")
    )

    # If the ancestor is in the primary nav, use that.
    for ancestor in ancestors:
        if ancestor in primary_nav:
            return ancestor

    # If none of the ancestors are in the primary nav, return nothing.
    return None


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
        "request": request,
    }
