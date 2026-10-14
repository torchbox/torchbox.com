from django.views import defaults
from django.views.decorators.cache import cache_control, never_cache

from tbx.core.utils.cache import get_default_cache_control_kwargs


@cache_control(**(get_default_cache_control_kwargs() | {"s_maxage": 600}))
def page_not_found(
    request, exception=None, template_name="patterns/pages/errors/404.html"
):
    return defaults.page_not_found(request, exception, template_name)


@never_cache
def server_error(request, template_name="patterns/pages/errors/500.html"):
    return defaults.server_error(request, template_name)
