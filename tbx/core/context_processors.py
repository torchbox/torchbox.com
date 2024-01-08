from django.conf import settings


def fb_app_id(request):
    return {
        "FB_APP_ID": settings.FB_APP_ID,
    }


def global_vars(request):
    return {
        "GOOGLE_TAG_MANAGER_ID": getattr(settings, "GOOGLE_TAG_MANAGER_ID", None),
    }
