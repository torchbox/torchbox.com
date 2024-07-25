from django.http import HttpResponseNotFound, HttpResponseServerError
from django.views import defaults
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.vary import vary_on_headers


def get_quality(media_type):
    return float(media_type.params.get("q", 1))


def show_html_error_page(request):
    accepted_types = sorted(request.accepted_types, key=get_quality, reverse=True)

    html_type = next(
        (
            accepted_type
            for accepted_type in accepted_types
            if accepted_type.match("text/html")
        ),
        None,
    )

    # If HTML isn't accepted, don't serve it
    if html_type is None:
        return False

    max_quality = get_quality(accepted_types[0])

    # If HTML isn't the highest quality, don't serve it
    if get_quality(html_type) < max_quality:
        return False

    return True


@vary_on_headers("Accept")
@requires_csrf_token
def page_not_found(
    request, exception=None, template_name="patterns/pages/errors/404.html"
):
    if show_html_error_page(request):
        return defaults.page_not_found(request, exception, template_name)

    # Serve a simpler, cheaper 404 page if we don't need to
    return HttpResponseNotFound(
        "Page not found", content_type="text/plain; charset=utf-8"
    )


@vary_on_headers("Accept")
@requires_csrf_token
def server_error(request, template_name="patterns/pages/errors/500.html"):
    if show_html_error_page(request):
        return defaults.server_error(request, template_name)

    # Serve a simpler, cheaper 500 page if we don't need to
    return HttpResponseServerError(
        "Server error", content_type="text/plain; charset=utf-8"
    )
