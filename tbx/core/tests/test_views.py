from django.test import TestCase, override_settings
from django.urls import reverse

from tbx.core.factories import HomePageFactory
from wagtail.models import Site


class SecurityViewTestCase(TestCase):
    url = reverse("security-txt")

    def test_accessible(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["security_txt"],
            "http://testserver/.well-known/security.txt",
        )
        self.assertIn("no-cache", response["Cache-Control"])


mode = "light"


class TestModeSwitcherView(TestCase):
    def test_view_sets_cookie(self):
        resp = self.client.get(
            reverse("switch_mode"), data=dict(switch_mode=mode, next_url="/")
        )
        self.assertEqual(resp.cookies["torchbox-mode"].value, mode)

    def test_view_redirects_to_original_url(self):
        resp = self.client.get(
            reverse("switch_mode"), data=dict(switch_mode=mode, next_url="/")
        )
        self.assertRedirects(resp, "/")

    def test_mode_is_set_on_subsequent_requests(self):
        self.client.get(
            reverse("switch_mode"),
            data=dict(switch_mode=mode, next_url="/"),
            headers={"accept": "text/html"},
        )

        resp = self.client.get("/")
        self.assertEqual(resp.context["MODE"], mode)

    def test_mode_cannot_be_outside_of_specific_values(self):
        resp = self.client.get(
            reverse("switch_mode"),
            data=dict(switch_mode="some random value", next_url="/"),
            headers={"accept": "text/html"},
        )

        self.assertEqual(resp.status_code, 401)

    def test_mode_cannot_be_set_without_query_params(self):
        resp = self.client.get(reverse("switch_mode"))
        self.assertEqual(resp.status_code, 401)

    def test_setting_random_mode_doesnt_work(self):
        # set valid mode
        self.client.get(
            reverse("switch_mode"),
            data=dict(switch_mode=mode, next_url="/"),
            headers={"accept": "text/html"},
        )

        # set invalid mode
        self.client.get(
            reverse("switch_mode"),
            data=dict(switch_mode="some random value", next_url="/"),
            headers={"accept": "text/html"},
        )

        resp = self.client.get("/")
        self.assertEqual(resp.context["MODE"], mode)

    @override_settings(
        BASE_DOMAIN="example.com",
    )
    def test_setting_theme_on_one_site_sets_it_on_multiple_sites(self):
        current_site = Site.objects.get(is_default_site=True)

        # change domain of default site
        current_site.hostname = "example.com"
        current_site.save()

        # create new information page
        new_home_page = HomePageFactory(title="New home page")

        # create new site
        new_site = Site.objects.create(
            hostname="new.example.com", root_page=new_home_page
        )

        # set theme on default site
        self.client.get(
            reverse("switch_mode"),
            data=dict(switch_mode=mode, next_url="/"),
        )

        # check theme is set on default site
        resp = self.client.get("/")
        self.assertEqual(resp.context["MODE"], mode)

        # check theme is set on new site
        resp = self.client.get(f"http://{new_site.hostname}/")
        self.assertEqual(resp.context["MODE"], mode)
