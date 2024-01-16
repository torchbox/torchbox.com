from django.test import TestCase

from tbx.people.factories import (
    AuthorFactory,
    ContactFactory,
    ContactReasonsListFactory,
)


class AuthorFactoryTestCase(TestCase):
    def test_author_factory(self):
        author = AuthorFactory()
        self.assertIsNotNone(author.name)
        self.assertIsNotNone(author.role)
        self.assertIsNone(author.person_page)
        self.assertIsNone(author.image)


class ContactFactoryTestCase(TestCase):
    def test_contact_factory(self):
        contact = ContactFactory()
        self.assertIsNotNone(contact.name)
        self.assertIsNotNone(contact.role)
        self.assertIsNotNone(contact.image)
        self.assertIsNotNone(contact.email_address)
        self.assertIsNotNone(contact.phone_number)


class ContactReasonsListFactoryTestCase(TestCase):
    def test_contact_reasons_list_factory(self):
        contact_reasons_list = ContactReasonsListFactory()
        self.assertIsNotNone(contact_reasons_list.name)
        self.assertIsNotNone(contact_reasons_list.heading)
        self.assertEqual(contact_reasons_list.reasons.count(), 0)

    def test_contact_reasons_list_factory_with_reasons(self):
        contact_reasons_list = ContactReasonsListFactory(reasons=4)
        self.assertIsNotNone(contact_reasons_list.name)
        self.assertIsNotNone(contact_reasons_list.heading)
        self.assertEqual(contact_reasons_list.reasons.count(), 4)
