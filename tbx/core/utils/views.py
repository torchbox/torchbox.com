from django.http import HttpResponseNotFound, HttpResponseServerError
from django.views import defaults
from django.views.decorators.vary import vary_on_headers


def show_html_error_page(request):
    """
    - If HTML is the most preferred type, show HTML.
    - If plain text is most preferred, don't show HTML
    - If neither are accepted, don't show HTML
    """
    return request.get_preferred_type(["text/html", "text/plain"]) == "text/html"


@vary_on_headers("Accept")
def page_not_found(request, exception, template_name="patterns/pages/errors/404.html"):
    if show_html_error_page(request):
        return defaults.page_not_found(request, exception, template_name)

    # Serve a simpler, cheaper 404 page if possible
    return HttpResponseNotFound(
        "Page not found", content_type="text/plain; charset=utf-8"
    )


@vary_on_headers("Accept")
def server_error(request, template_name="patterns/pages/errors/500.html"):
    if show_html_error_page(request):
        return defaults.server_error(request, template_name)

    # Serve a simpler, cheaper 500 page if possible
    return HttpResponseServerError(
        "Server error", content_type="text/plain; charset=utf-8"
    )
