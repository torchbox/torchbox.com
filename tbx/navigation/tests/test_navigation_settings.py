from django.test import SimpleTestCase

from wagtail.admin.panels.base import get_form_for_model

from tbx.navigation.models import NavigationSettings


class NavigationSettingsFormTestCase(SimpleTestCase):
    def setUp(self):
        self.form_class = get_form_for_model(
            NavigationSettings,
            fields=[
                "footer_newsletter_cta_url",
                "footer_newsletter_cta_text",
            ],
        )

    def test_cta_optional(self):
        form = self.form_class(
            data={"footer_newsletter_cta_url": "", "footer_newsletter_cta_text": ""}
        )
        self.assertTrue(form.is_valid())

    def test_cta_text_required_if_url_supplied(self):
        form = self.form_class(
            data={
                "footer_newsletter_cta_url": "https://example.com",
                "footer_newsletter_cta_text": "",
            }
        )
        self.assertFormError(
            form,
            "footer_newsletter_cta_text",
            "The CTA footer text is required when a URL is supplied",
        )
