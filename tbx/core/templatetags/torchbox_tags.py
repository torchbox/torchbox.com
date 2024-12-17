from django import template
from django.conf import settings

from tbx.blog.models import BlogPage
from tbx.core.models import MainMenu

register = template.Library()


@register.simple_tag
def get_popular_tags(model):
    return model.get_popular_tags()


# settings value
@register.simple_tag
def get_googe_maps_key():
    return getattr(settings, "GOOGLE_MAPS_KEY", "")


@register.simple_tag
def get_next_sibling_by_order(page):
    sibling = page.get_next_siblings().live().public().first()

    if sibling:
        return sibling.specific


@register.simple_tag
def get_prev_sibling_by_order(page):
    sibling = page.get_prev_siblings().live().public().first()

    if sibling:
        return sibling.specific


@register.simple_tag
def get_next_sibling_blog(page):
    sibling = (
        BlogPage.objects.filter(date__lt=page.date).order_by("-date").live().public().first()
    )
    if sibling:
        return sibling.specific


@register.simple_tag
def get_prev_sibling_blog(page):
    sibling = (
        BlogPage.objects.filter(date__gt=page.date).order_by("-date").live().public().last()
    )
    if sibling:
        return sibling.specific


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return context["request"].site.root_page


@register.filter
def content_type(value):
    return value.__class__.__name__.lower()


@register.simple_tag
def main_menu():
    return MainMenu.objects.first()


# Format times e.g. on event page
@register.filter
def time_display(time):
    # Get hour and minute from time object
    hour = time.hour
    minute = time.minute

    # Convert to 12 hour format
    if hour >= 12:
        pm = True
        hour -= 12
    else:
        pm = False
    if hour == 0:
        hour = 12

    # Hour string
    hour_string = str(hour)

    # Minute string
    if minute != 0:
        minute_string = "." + str(minute)
    else:
        minute_string = ""

    # PM string
    if pm:
        pm_string = "pm"
    else:
        pm_string = "am"

    # Join and return
    return "".join([hour_string, minute_string, pm_string])
