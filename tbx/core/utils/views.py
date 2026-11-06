from django.views import defaults
from django.views.decorators.cache import never_cache


@never_cache
def page_not_found(request, exception, template_name="patterns/pages/errors/404.html"):
    return defaults.page_not_found(request, exception, template_name)


@never_cache
def server_error(request, template_name="patterns/pages/errors/500.html"):
    return defaults.server_error(request, template_name)
