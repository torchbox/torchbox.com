import json

from django.conf import settings

from tbx.core.models import ImportantPageSettings


def global_vars(request):
    # Read the mode cookie to determine the user's saved preference for light or dark mode, if it exists
    # Ensure it is one of the allowed values
    mode = request.COOKIES.get("torchbox-mode", "dark")
    if mode not in settings.ALLOWED_MODES:
        mode = "dark"

    return {
        "GOOGLE_TAG_MANAGER_ID": getattr(settings, "GOOGLE_TAG_MANAGER_ID", None),
        "SEO_NOINDEX": settings.SEO_NOINDEX,
        "COOKIE_POLICY_PAGE": ImportantPageSettings.for_request(
            request
        ).cookie_policy_page,
        "CARBON_EMISSIONS_PAGE": ImportantPageSettings.for_request(
            request
        ).carbon_emissions_page,
        "ALLOWED_MODES": json.dumps(settings.ALLOWED_MODES),
        "MODE": mode,
        "BASE_DOMAIN": settings.BASE_DOMAIN,
    }
