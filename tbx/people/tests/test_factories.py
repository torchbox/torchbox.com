from django.test import TestCase

from tbx.core.factories import HomePageFactory, StandardPageFactory
from tbx.core.models import StandardPage
from tbx.people.factories import (
    AuthorFactory,
    ContactFactory,
    ContactReasonsListFactory,
    PersonIndexPageFactory,
    PersonPageFactory,
)
from tbx.taxonomy.factories import TeamFactory
from tbx.taxonomy.models import Team


class ContactFactoryTestCase(TestCase):
    def test_contact_factory(self):
        contact = ContactFactory()
        self.assertIsNotNone(contact.title)
        self.assertIsNotNone(contact.text)
        self.assertIsNotNone(contact.name)
        self.assertIsNotNone(contact.role)
        self.assertIsNotNone(contact.image)

        # cta should be empty
        self.assertEqual(contact.cta.get_prep_value(), [])

    def test_contact_factory_with_cta_external_link(self):
        contact = ContactFactory(cta={"link_type": "external_link"})
        self.assertIsNotNone(contact.title)
        self.assertIsNotNone(contact.text)
        self.assertIsNotNone(contact.name)
        self.assertIsNotNone(contact.role)
        self.assertIsNotNone(contact.image)

        # cta shouldn't be empty
        cta_content = contact.cta.get_prep_value()
        self.assertNotEqual(cta_content, [])

        button_link_data = cta_content[0]["value"]["button_link"]
        # we expect a single block
        self.assertEqual(len(button_link_data), 1)
        # the block type is external_link
        self.assertEqual(button_link_data[0]["type"], "external_link")

    def test_contact_factory_with_cta_email(self):
        contact = ContactFactory(cta={"link_type": "email"})
        self.assertIsNotNone(contact.title)
        self.assertIsNotNone(contact.text)
        self.assertIsNotNone(contact.name)
        self.assertIsNotNone(contact.role)
        self.assertIsNotNone(contact.image)

        # cta shouldn't be empty
        cta_content = contact.cta.get_prep_value()
        self.assertNotEqual(cta_content, [])

        button_link_data = cta_content[0]["value"]["button_link"]
        # we expect a single block
        self.assertEqual(len(button_link_data), 1)
        # the block type is email
        self.assertEqual(button_link_data[0]["type"], "email")

    def test_contact_factory_with_cta_internal_link(self):
        contact = ContactFactory(cta={"link_type": "internal_link"})
        self.assertIsNotNone(contact.title)
        self.assertIsNotNone(contact.text)
        self.assertIsNotNone(contact.name)
        self.assertIsNotNone(contact.role)
        self.assertIsNotNone(contact.image)

        # cta shouldn't be empty
        cta_content = contact.cta.get_prep_value()
        self.assertNotEqual(cta_content, [])

        button_link_data = cta_content[0]["value"]["button_link"]
        # we expect a single block
        self.assertEqual(len(button_link_data), 1)
        # the block type is internal_link
        self.assertEqual(button_link_data[0]["type"], "internal_link")
        # if we don't specify the page, and there's no homepage
        # a standardpage is created and used as the internal_link
        self.assertTrue(
            StandardPage.objects.filter(pk=button_link_data[0]["value"]).exists()
        )
        # on the other hand, if a homepage exists, it's used as the internal_link
        homepage = HomePageFactory()
        another_contact = ContactFactory(cta={"link_type": "internal_link"})
        cta_content = another_contact.cta.get_prep_value()
        button_link_data = cta_content[0]["value"]["button_link"]
        self.assertEqual(button_link_data[0]["value"], homepage.pk)

    def test_contact_factory_with_cta_internal_link_specified(self):
        standard_page = StandardPageFactory()
        contact = ContactFactory(
            cta={"link_type": "internal_link", "page": standard_page}
        )
        self.assertIsNotNone(contact.title)
        self.assertIsNotNone(contact.text)
        self.assertIsNotNone(contact.name)
        self.assertIsNotNone(contact.role)
        self.assertIsNotNone(contact.image)

        # cta shouldn't be empty
        cta_content = contact.cta.get_prep_value()
        self.assertNotEqual(cta_content, [])

        button_link_data = cta_content[0]["value"]["button_link"]
        # we expect a single block
        self.assertEqual(len(button_link_data), 1)
        # the block type is internal_link, whose value is the the specified page's pk
        self.assertEqual(button_link_data[0]["type"], "internal_link")
        self.assertEqual(button_link_data[0]["value"], standard_page.pk)


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


class AuthorFactoryTestCase(TestCase):
    def test_author_factory(self):
        author = AuthorFactory()
        self.assertIsNotNone(author.name)
        self.assertIsNotNone(author.role)
        self.assertIsNotNone(author.image)


class PersonIndexPageFactoryTestCase(TestCase):
    def test_person_index_page_factory(self):
        person_index_page = PersonIndexPageFactory()
        self.assertIsNotNone(person_index_page.title)
        self.assertIsNotNone(person_index_page.strapline)


class PersonPageFactoryTestCase(TestCase):
    def test_person_page_factory(self):
        person_page = PersonPageFactory()
        self.assertIsNotNone(person_page.title)
        self.assertIsNotNone(person_page.role)
        self.assertIsNotNone(person_page.biography)
        self.assertIsNotNone(person_page.image)
        self.assertEqual(person_page.related_teams.count(), 1)

    def test_person_page_factory_with_related_team(self):
        self.assertEqual(Team.objects.count(), 0)

        # related_teams as a string
        jane = PersonPageFactory(title="Jane Doe", related_teams="Engineering")
        self.assertEqual(jane.related_teams.count(), 1)
        self.assertEqual(jane.related_teams.first().name, "Engineering")

        # related_teams as a `Team` instance
        team = TeamFactory(name="Digital Marketing")
        john = PersonPageFactory(title="John Doe", related_teams=team)
        self.assertEqual(john.related_teams.count(), 1)
        self.assertEqual(john.related_teams.first().name, "Digital Marketing")

        self.assertEqual(Team.objects.count(), 2)
