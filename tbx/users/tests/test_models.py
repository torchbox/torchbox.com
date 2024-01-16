from django.test import TestCase

from tbx.users.factories import UserFactory


class TestUserFactory(TestCase):
    def test_create(self):
        UserFactory()
