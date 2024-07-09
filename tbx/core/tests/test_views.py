from django.test import TestCase
from django.urls import reverse


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
        self.assertEquals(resp.cookies["torchbox-mode"].value, mode)

    def test_view_redirects_to_original_url(self):
        resp = self.client.get(
            reverse("switch_mode"), data=dict(switch_mode=mode, next_url="/")
        )
        self.assertRedirects(resp, "/")

    def test_mode_is_set_on_subsequent_requests(self):
        self.client.get(
            reverse("switch_mode"),
            data=dict(switch_mode=mode, next_url="/"),
            HTTP_Accept="text/html",
        )

        resp = self.client.get("/")
        self.assertEqual(resp.context["MODE"], mode)

    def test_mode_cannot_be_outside_of_specific_values(self):
        resp = self.client.get(
            reverse("switch_mode"),
            data=dict(switch_mode="some random value", next_url="/"),
            HTTP_Accept="text/html",
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
            HTTP_Accept="text/html",
        )

        # set invalid mode
        self.client.get(
            reverse("switch_mode"),
            data=dict(switch_mode="some random value", next_url="/"),
            HTTP_Accept="text/html",
        )

        resp = self.client.get("/")
        self.assertEqual(resp.context["MODE"], mode)
