import logging
from datetime import timedelta

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

import requests
from tbx.core.errors import UnauthorizedHTTPError
from tbx.core.forms import ModeSwitcherForm

logger = logging.getLogger(__name__)


def newsletter_subsribe(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest" and request.GET.get(
        "email"
    ):
        requests.post(
            "https://us10.api.mailchimp.com/2.0/lists/subscribe",
            json={
                "apikey": settings.MAILCHIMP_KEY,
                "id": settings.MAILCHIMP_MAILING_LIST_ID,
                "email": {"email": request.GET.get("email")},
            },
        )
    return HttpResponse()


def robots(request):
    content = "\n".join(
        [
            "User-Agent: *",
            "Disallow: /search/",
            "Allow: /",
        ]
    )
    return HttpResponse(content, content_type="text/plain")


@method_decorator(never_cache, name="dispatch")
class SecurityView(TemplateView):
    template_name = "security.txt"
    content_type = "text/plain"

    expires = timedelta(days=7)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["security_txt"] = self.request.build_absolute_uri(self.request.path)
        context["expires"] = (
            (timezone.now() + self.expires).replace(microsecond=0).isoformat()
        )
        return context


def switch_mode(request):
    form = ModeSwitcherForm(request.GET)

    try:
        if not form.is_valid():
            raise UnauthorizedHTTPError

        new_mode = form.cleaned_data["switch_mode"]

        next_url = form.cleaned_data["next_url"]
        if not next_url:
            raise UnauthorizedHTTPError

        if url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts=settings.ALLOWED_HOSTS,
            require_https=request.is_secure(),
        ):
            response = redirect(next_url)
        else:
            logger.warning(
                f"Different domain url registered in switch_theme view, got next_url: {next_url}"
            )
            response = HttpResponseNotFound()
        response.set_cookie(
            "torchbox-mode",
            new_mode,
            max_age=365 * 24 * 60 * 60,
            path="/",
        )
        return response
    except UnauthorizedHTTPError:
        return HttpResponse(status=401)
