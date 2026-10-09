from django.test import TestCase
from django.urls import reverse


class TestSearch(TestCase):
    def setUp(self):
        self.url = reverse("search")

    def test_search(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Search")

    def test_search__valid(self):
        response = self.client.get(self.url + "?query=abc")
        self.assertEqual(response.status_code, 200)

    def test_search__with_null_character(self):
        response = self.client.get(self.url + "?query=abc%00")
        self.assertEqual(response.status_code, 200)
