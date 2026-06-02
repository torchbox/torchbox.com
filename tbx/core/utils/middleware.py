from typing import TYPE_CHECKING, Optional

from django.http import Http404, HttpResponseRedirect

from wagtail.models import Site


if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from wagtail.models import Page


class URLCaseNormalizeMiddleware:
    """
    If Wagtail can't find a page, this middleware checks whether a lower-case
    version of the page exists too, and redirects to it
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def get_page_for_path(
        self, site: Site, request: "HttpRequest", path: str
    ) -> Optional["Page"]:
        """
        Implementation lifted from `wagtail.views.serve`.
        """

        path_components = [component for component in path.split("/") if component]

        try:
            page, _, _ = site.root_page.localized.specific.route(
                request, path_components
            )
        except Http404:
            return None

        return page

    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        response = self.get_response(request)

        if response.status_code != 404:
            return response

        # If the path is already lower-case, do nothing.
        if request.path == request.path.lower():
            return response

        # Pre-confirm there's a site for this URL
        site = Site.find_for_request(request)
        if not site:
            return response

        if self.get_page_for_path(site, request, request.path.lower()):
            query_string = f"?{request.GET.urlencode()}" if request.GET else ""
            return HttpResponseRedirect(request.path.lower() + query_string)

        return response
