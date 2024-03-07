from django.test import TestCase

from tbx.core.factories import HomePageFactory
from tbx.images.factories import CustomImageFactory
from tbx.people.models import Author, PersonIndexPage, PersonPage
from tbx.taxonomy.factories import TeamFactory
from wagtail.models import Page, Site


class TestAuthor(TestCase):
    def setUp(self):
        super().setUp()

        site = Site.objects.get(is_default_site=True)
        root = Page.objects.get(depth=1)
        home = HomePageFactory(title="Torchbox", parent=root)

        site.root_page = home
        site.save()

        self.personindex = PersonIndexPage(
            title="Team",
            strapline="This is us, the people that make Torchbox",
        )
        home.add_child(instance=self.personindex)
        self.personindex.save()

    def test_author_created_when_personpage_published(self):
        self.assertEqual(Author.objects.count(), 0)

        person = PersonPage(
            title="Juliet Jacques",
            role="Tinkerer",
            biography="<p>Meet JJ, the tinkerer extraordinaire, turning junk into genius with a wink and a wrench!</p>",
            image=CustomImageFactory(),
        )
        self.personindex.add_child(instance=person)
        person.save()
        person.related_teams.add(TeamFactory(name="Engineering"))
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
        person = PersonPage(
            title="Koldo Knightley",
            role="Culinary Connoisseur",
            biography="<p>With a spatula in hand and a sprinkle of spice, KK orchestrates culinary masterpieces that tantalize taste buds and delight diners.</p>",
            image=CustomImageFactory(),
        )
        self.personindex.add_child(instance=person)
        person.save()
        person.related_teams.add(TeamFactory(name="Food and Beverage"))
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
        person = PersonPage(
            title="Greta Goodman",
            role="Gadget Guru",
            biography="<p>Greta transforms futuristic ideas into reality with flair and finesse.</p>",
            image=CustomImageFactory(),
        )
        self.personindex.add_child(instance=person)
        person.save()
        person.related_teams.add(TeamFactory(name="Gadgetry"))
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
        person = PersonPage(
            title="Giovanni Grant",
            role="Fitness Trainer",
            biography="<p>Giovanni empowers the team to achieve peak performance and unlock their full potential.</p>",
            image=CustomImageFactory(),
        )
        self.personindex.add_child(instance=person)
        person.save()
        person.related_teams.add(TeamFactory(name="Fitness"))
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
