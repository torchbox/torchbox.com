from django.test import TestCase

from tbx.blog.factories import BlogIndexPageFactory, BlogPageFactory
from tbx.core.factories import HomePageFactory, StandardPageFactory
from tbx.people.factories import ContactFactory
from tbx.people.models import Contact
from tbx.work.factories import (
    HistoricalWorkPageFactory,
    WorkIndexPageFactory,
    WorkPageFactory,
)
from wagtail.models import Site


class TestContact(TestCase):
    def setUp(self):
        super().setUp()

        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        self.home = HomePageFactory(parent=root)

        site.root_page = self.home
        site.save()

        self.blogindex = BlogIndexPageFactory(title="Blog", parent=self.home)
        self.workindex = WorkIndexPageFactory(title="Work", parent=self.home)
        self.contact = ContactFactory(cta={"link_type": "email"})

    def test_one_default_contact(self):
        """
        Only 1 default contact can exist at any given time
        """
        ContactFactory.create_batch(size=2, cta={"link_type": "external_link"})

        self.assertEqual(Contact.objects.filter(default_contact=True).count(), 0)

        self.contact.default_contact = True
        self.contact.save()
        self.contact.refresh_from_db()

        self.assertTrue(self.contact.default_contact)

        # Now, let's create another contact and mark it as the default contact
        another_contact = ContactFactory(default_contact=True)
        # We still expect to only have 1 default contact, and it should be `another_contact`
        self.contact.refresh_from_db()
        self.assertEqual(Contact.objects.filter(default_contact=True).count(), 1)
        self.assertTrue(another_contact.default_contact)
        self.assertFalse(self.contact.default_contact)

    def test_contact_link(self):
        # self.contact was created with a link_type of 'email'
        self.assertTrue(self.contact.link.startswith("mailto:"))

        # Let's create a contact with link_type 'external_link'
        contact2 = ContactFactory(cta={"link_type": "external_link"})
        self.assertTrue(contact2.link.startswith("http"))

        # Let's create a contact with link_type 'internal_link'
        contact3 = ContactFactory(
            cta={"link_type": "internal_link", "page": self.workindex}
        )
        self.assertEqual(contact3.link, self.workindex.url)

    def test_no_contact_specified_on_any_page(self):
        for page in [self.home, self.blogindex, self.workindex]:
            self.assertIsNone(page.contact)
            self.assertIsNone(page.footer_contact)

        blog = BlogPageFactory(parent=self.blogindex)
        self.assertIsNone(blog.contact)
        self.assertIsNone(blog.footer_contact)

        work = WorkPageFactory(parent=self.workindex)
        self.assertIsNone(work.contact)
        self.assertIsNone(work.footer_contact)

        std_page = StandardPageFactory(parent=work)
        self.assertIsNone(std_page.contact)
        self.assertIsNone(std_page.footer_contact)

    def test_contact_specified_on_homepage(self):
        self.home.contact = self.contact
        self.home.save()
        self.home.refresh_from_db()

        self.assertEqual(self.home.contact, self.contact)
        self.assertEqual(self.home.footer_contact, self.contact)

        self.assertIsNone(self.blogindex.contact)
        self.assertEqual(self.blogindex.footer_contact, self.contact)

        self.assertIsNone(self.workindex.contact)
        self.assertEqual(self.workindex.footer_contact, self.contact)

        blog = BlogPageFactory(parent=self.blogindex)
        self.assertIsNone(blog.contact)
        self.assertEqual(blog.footer_contact, self.contact)

        work = WorkPageFactory(parent=self.workindex)
        self.assertIsNone(work.contact)
        self.assertEqual(work.footer_contact, self.contact)

        std_page = StandardPageFactory(parent=work)
        self.assertIsNone(std_page.contact)
        self.assertEqual(std_page.footer_contact, self.contact)

    def test_contact_specified_on_an_indexpage(self):
        self.blogindex.contact = self.contact
        self.blogindex.save()
        self.blogindex.refresh_from_db()

        self.assertIsNone(self.home.contact)
        self.assertIsNone(self.home.footer_contact)

        self.assertEqual(self.blogindex.contact, self.contact)
        self.assertEqual(self.blogindex.footer_contact, self.contact)

        # child of blogindex
        blog = BlogPageFactory(parent=self.blogindex)
        self.assertIsNone(blog.contact)
        self.assertEqual(blog.footer_contact, self.contact)

        # grandchild of blogindex
        std_page = StandardPageFactory(parent=blog)
        self.assertIsNone(std_page.contact)
        self.assertEqual(std_page.footer_contact, self.contact)

    def test_contact_specified_on_descendants(self):
        self.workindex.contact = self.contact
        self.workindex.save()
        self.workindex.refresh_from_db()

        self.assertIsNone(self.home.contact)
        self.assertIsNone(self.home.footer_contact)

        self.assertIsNone(self.blogindex.contact)
        self.assertIsNone(self.blogindex.footer_contact)

        self.assertEqual(self.workindex.contact, self.contact)
        self.assertEqual(self.workindex.footer_contact, self.contact)

        # child of workindex
        work = HistoricalWorkPageFactory(parent=self.workindex)
        self.assertIsNone(work.contact)
        self.assertEqual(work.footer_contact, self.contact)

        # another child of workindex, this time we specify another contact
        jane_doe = ContactFactory(name="Jane Doe", cta={"link_type": "external_link"})
        morework = HistoricalWorkPageFactory(parent=self.workindex, contact=jane_doe)

        self.assertEqual(morework.contact, jane_doe)
        self.assertEqual(morework.footer_contact, jane_doe)
        # sibling shouldn't be affected
        self.assertIsNone(work.contact)
        self.assertEqual(work.footer_contact, self.contact)
        # parent shouldn't be affected
        self.assertEqual(self.workindex.contact, self.contact)
        self.assertEqual(self.workindex.footer_contact, self.contact)

        # child of morework
        std_page = StandardPageFactory(parent=morework)
        # `footer_contact` should be inherited from parent
        self.assertEqual(std_page.footer_contact, jane_doe)
        # but `contact` should remain unset
        self.assertIsNone(std_page.contact)

    def test_footer_contact_when_default_contact_exists(self):
        """
        If a default contact exists, a page's `footer_contact` property should return that contact,
        even if neither the page nor any of its ancestors have a `contact` specified.
        """
        self.assertEqual(Contact.objects.filter(default_contact=True).count(), 0)

        self.contact.default_contact = True
        self.contact.save()
        self.contact.refresh_from_db()

        self.assertTrue(self.contact.default_contact)

        for page in [self.home, self.blogindex, self.workindex]:
            self.assertIsNone(page.contact)
            self.assertTrue(page.footer_contact)
            self.assertEqual(page.footer_contact, self.contact)
