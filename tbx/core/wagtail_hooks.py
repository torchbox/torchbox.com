from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import redirect
from django.templatetags.static import static
from django.utils.cache import add_never_cache_headers
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from wagtail import hooks
from wagtail.documents import get_document_model
from wagtail.documents.models import document_served
from wagtail.images.image_operations import FilterOperation

from PIL import ImageEnhance
from storages.backends.s3 import S3Storage


@hooks.register("before_serve_document", order=100)
def serve_document_from_s3(document, request):
    # Skip this hook if not using django-storages boto3 backend.
    if not issubclass(default_storage, S3Storage):
        return

    # Send document_served signal.
    document_served.send(
        sender=get_document_model(), instance=document, request=request
    )

    # Get direct S3 link.
    file_url = document.file.url

    # Generate redirect response and add never_cache headers.
    response = redirect(file_url)
    del response["Cache-control"]
    add_never_cache_headers(response)
    return response


@hooks.register("construct_settings_menu")
def hide_main_menu_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if item.name != "main-menu"]


@hooks.register("insert_global_admin_js")
def hotjar_admin_tracking():
    """
    Trial Hotjar tracking for the CMS admin. Testing whether
    this can help with Wagtail core design decisions.
    """
    hjid = settings.ADMIN_HOTJAR_SITE_ID

    if not hjid:
        return ""

    return mark_safe(  # noqa: S308
        f"""
    <script>
        (function(h,o,t,j,a,r){{
            h.hj=h.hj||function(){{(h.hj.q=h.hj.q||[]).push(arguments)}};
            h._hjSettings={{hjid:{hjid},hjsv:6}};
            a=o.getElementsByTagName('head')[0];
            r=o.createElement('script');r.async=1;
            r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
            a.appendChild(r);
        }})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
    </script>
    """
    )


@hooks.register("insert_global_admin_js", order=100)
def admin_config():
    """Add /static/js/admin.js to the admin."""
    return format_html('<script src="{}"></script>', static("js/admin.js"))


class ReduceSaturationOperation(FilterOperation):
    def construct(self, factor):
        self.factor = float(factor)

    def run(self, willow, image, env):
        enhancer = ImageEnhance.Color(willow.image)
        willow.image = enhancer.enhance(self.factor)
        return willow


@hooks.register("register_image_operations")
def register_image_operations():
    return [
        ("saturation", ReduceSaturationOperation),
    ]
