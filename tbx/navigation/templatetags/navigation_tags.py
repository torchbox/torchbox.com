from django import template

register = template.Library()


# Primary nav snippets
@register.inclusion_tag(
    "patterns/navigation/components/primary-nav.html", takes_context=True
)
def primarynav(context, is_home, is_desktop):
    request = context["request"]
    return {
        "primarynav": context["settings"]["navigation"][
            "NavigationSettings"
        ].primary_navigation,
        "job_count": context.get("job_count", 0),
        "request": request,
        "is_home": is_home,
        "is_desktop": is_desktop,
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
