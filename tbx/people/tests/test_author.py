from django.test import TestCase

from tbx.core.factories import HomePageFactory
from tbx.people.factories import PersonIndexPageFactory, PersonPageFactory
from tbx.people.models import Author
from wagtail.models import Page, Site


class TestAuthor(TestCase):
    def setUp(self):
        super().setUp()

        site = Site.objects.get(is_default_site=True)
        root = Page.objects.get(depth=1)
        home = HomePageFactory(title="Torchbox", parent=root)

        site.root_page = home
        site.save()

        self.personindex = PersonIndexPageFactory(
            parent=home,
        )

    def test_author_created_when_personpage_published(self):
        self.assertEqual(Author.objects.count(), 0)

        person = PersonPageFactory(parent=self.personindex)
        revision = person.save_revision()
        # Publish the page to trigger the page_published signal
        revision.publish()

        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.first()
        self.assertEqual(author.person_page, person)
        self.assertEqual(author.name, person.title)
        self.assertEqual(author.role, person.role)
        self.assertEqual(author.image, person.image)

    def test_author_updated_when_personpage_updated(self):
        person = PersonPageFactory(
            parent=self.personindex,
            title="Koldo Knightley",
        )
        person.save_revision().publish()

        author = Author.objects.get(person_page=person)

        # Check that the author's name is the person page's title
        self.assertEqual(author.name, "Koldo Knightley")

        # Now let's update the person page's title and publish it again
        person.title = "Koldo “KK” Knightley"
        person.save_revision().publish()

        # The author's name should now be updated to reflect the new title
        author.refresh_from_db()
        self.assertEqual(author.name, "Koldo “KK” Knightley")

    def test_author_remains_when_personpage_unpublished(self):
        person = PersonPageFactory(parent=self.personindex)
        person.save_revision().publish()

        self.assertEqual(Author.objects.count(), 1)

        person.unpublish()

        # The Author should still exist
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.first()
        self.assertEqual(author.person_page, person)
        self.assertEqual(author.name, person.title)
        self.assertEqual(author.role, person.role)
        self.assertEqual(author.image, person.image)

    def test_author_remains_when_personpage_deleted(self):
        person = PersonPageFactory(parent=self.personindex)
        person.save_revision().publish()

        self.assertEqual(Author.objects.count(), 1)

        person.delete()

        # The Author should still exist
        self.assertEqual(Author.objects.count(), 1)
        author = Author.objects.first()
        self.assertIsNone(author.person_page)
        self.assertEqual(author.name, person.title)
        self.assertEqual(author.role, person.role)
        self.assertEqual(author.image, person.image)
