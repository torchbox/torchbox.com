from django.conf import settings

from tbx.core.models import ImportantPageSettings


def global_vars(request):
    return {
        "GOOGLE_TAG_MANAGER_ID": getattr(settings, "GOOGLE_TAG_MANAGER_ID", None),
        "SEO_NOINDEX": settings.SEO_NOINDEX,
        "COOKIE_POLICY_PAGE": ImportantPageSettings.for_request(
            request
        ).cookie_policy_page,
        "CARBON_EMISSIONS_PAGE": ImportantPageSettings.for_request(
            request
        ).carbon_emissions_page,
    }
