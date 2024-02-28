from django import template
from django.utils.text import camel_case_to_spaces, slugify

from tbx.core.utils.models import SocialMediaSettings

register = template.Library()


# Social text
@register.filter(name="social_text")
def social_text(page, site):
    try:
        return page.social_text
    except AttributeError:
        return SocialMediaSettings.for_site(site).default_sharing_text


# Get widget type of a field
@register.filter(name="widget_type")
def widget_type(bound_field):
    return slugify(camel_case_to_spaces(bound_field.field.widget.__class__.__name__))


@register.simple_tag(takes_context=True)
def social_media_settings(context):
    return SocialMediaSettings.for_request(request=context["request"])


@register.simple_tag()
def format_date_for_event(start_date, start_time=None, end_date=None, end_time=None):
    def format_time(time):
        if time.minute == 0:
            return time.strftime("%I").lstrip("0")
        else:
            return time.strftime("%I:%M").lstrip("0")

    formatted_start_date = start_date.strftime("%d %b %Y")

    if start_time:
        formatted_start_date += f", {format_time(start_time)}"

        if end_date:
            if start_date == end_date:
                if end_time:
                    if start_time != end_time:
                        if start_time.strftime("%p") == end_time.strftime("%p"):
                            formatted_start_date += f"-{format_time(end_time)}{end_time.strftime('%p').lower()}"
                        else:
                            formatted_start_date += f"{start_time.strftime('%p').lower()}-{format_time(end_time)}{end_time.strftime('%p').lower()}"
                    else:
                        formatted_start_date += start_time.strftime("%p").lower()
                else:
                    formatted_start_date += start_time.strftime("%p").lower()
            else:
                formatted_start_date += start_time.strftime("%p").lower()
                if end_time:
                    formatted_start_date += f" - {end_date.strftime('%d %b %Y')}, {format_time(end_time)}{end_time.strftime('%p').lower()}"
                else:
                    formatted_start_date += f" - {end_date.strftime('%d %b %Y')}"
        else:
            formatted_start_date += start_time.strftime("%p").lower()
    elif end_date:
        formatted_start_date += f" - {end_date.strftime('%d %b %Y')}"
    return formatted_start_date
