import json

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag(takes_context=True)
def blog_posting_jsonld(context):
    """Return the BlogPosting JSON-LD structured data as JSON."""
    page = context.get("page")
    request = context.get("request")
    if page and hasattr(page, "get_blog_posting_jsonld"):
        return mark_safe(json.dumps(page.get_blog_posting_jsonld(request), indent=4))  # noqa: S308
    return ""
