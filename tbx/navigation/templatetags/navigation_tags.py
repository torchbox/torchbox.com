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


# Primary nav mobile snippet
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
