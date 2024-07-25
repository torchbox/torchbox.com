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


class PageNotFoundTestCase(TestCase):
    url = "/does-not-exist/"

    def test_accessible(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("text/html", response.headers["content-type"])

    def test_accept_html(self) -> None:
        response = self.client.get(self.url, headers={"Accept": "text/html"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("text/html", response.headers["content-type"])

    def test_simple_when_doesnt_accept_html(self) -> None:
        response = self.client.get(self.url, headers={"Accept": "text/css"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("text/plain", response.headers["content-type"])

    def test_simple_when_html_not_highest(self) -> None:
        response = self.client.get(
            self.url, headers={"Accept": "text/html;q=0.8,text/css"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("text/plain", response.headers["content-type"])
