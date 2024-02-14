I have updated the `footer_contact` property in 07cadd4. In the snippet below, `footer_contact` is the previous version, and `footer_contact_improved` is the updated version.

```python

    @cached_property
    def footer_contact(self):
        """
        Use the page's own contact if set, otherwise, derive the contact from
        its ancestors, and finally fall back to the default contact.

        NOTE: if, for some reason, a default contact doesn't exist, this will
        return None, in which case, we'll not display the block in the footer template.
        """
        if contact := self.contact:
            return contact

        # _in theory_, there should only be one Contact object with default_contact=True.
        # (see `tbx.people.models.Contact.save()`)
        default_contact = Contact.objects.filter(default_contact=True).first()

        try:
            return next(
                p.contact
                for p in self.get_ancestors().specific().order_by("-depth")
                if getattr(p, "contact", None) is not None
            )
        except StopIteration:
            return default_contact

    @cached_property
    def footer_contact_improved(self):
        """
        Use the page's own contact if set, otherwise, derive the contact from
        its ancestors, and finally fall back to the default contact.

        NOTE: if, for some reason, a default contact doesn't exist, this will
        return None, in which case, we'll not display the block in the footer template.
        """
        if contact := self.contact:
            return contact

        ancestors = (
            self.get_ancestors().defer_streamfields().specific().order_by("-depth")
        )
        for ancestor in ancestors:
            if getattr(ancestor, "contact_id", None) is not None:
                return ancestor.contact

        # _in theory_, there should only be one Contact object with default_contact=True.
        # (see `tbx.people.models.Contact.save()`)
        return Contact.objects.filter(default_contact=True).first()
```

I did some testing to investigate the number of queries:

```python
# tbx/people/tests/test_contact.py
import time

from django.db import connection
from django.test import TestCase

from tabulate import tabulate # pip install tabulate
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


class QueryLogger:
    # Reference: https://docs.djangoproject.com/en/4.2/topics/db/instrumentation/
    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        current_query = {"sql": sql, "params": params, "many": many}
        start = time.monotonic()
        try:
            result = execute(sql, params, many, context)
        except Exception as e:
            current_query["status"] = "error"
            current_query["exception"] = e
            raise
        else:
            current_query["status"] = "ok"
            return result
        finally:
            duration = time.monotonic() - start
            current_query["duration"] = duration
            self.queries.append(current_query)

    def render(self):
        if self.queries:
            # Add a counter column
            for i, d in enumerate(self.queries, start=1):
                d["Query №"] = i

            headers = self.queries[0].keys()
            rows = [[row[header] for header in headers] for row in self.queries]

            print(tabulate(rows, headers=headers, tablefmt="pipe"))

        else:
            print(f"{len(self.queries)} queries\n\n")

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

    # .... other tests ....
    # .....................

    def test_queries(self):
        self.home.contact = self.contact
        self.home.save()
        self.home.refresh_from_db()
        jane_doe = ContactFactory(name="Jane Doe", cta={"link_type": "external_link"})
        work = HistoricalWorkPageFactory(parent=self.workindex, contact=jane_doe)

        # -------------------------------------------------
        # with self.assertNumQueries(5):
        #     self.workindex.footer_contact

        ql = QueryLogger()
        with connection.execute_wrapper(ql):
            self.workindex.footer_contact
        print("### 1. self.workindex.footer_contact\n\n")
        ql.render()

        # -------------------------------------------------
        # with self.assertNumQueries(4):
        #     self.workindex.footer_contact_improved

        ql = QueryLogger()
        with connection.execute_wrapper(ql):
            self.workindex.footer_contact_improved
        print("### 2. self.workindex.footer_contact_improved\n\n")
        ql.render()

        # -------------------------------------------------
        # with self.assertNumQueries(0):
        #     work.footer_contact

        ql = QueryLogger()
        with connection.execute_wrapper(ql):
            work.footer_contact
        print("### 3. work.footer_contact\n\n")
        ql.render()

        # -------------------------------------------------
        # with self.assertNumQueries(0):
        #     work.footer_contact_improved

        ql = QueryLogger()
        with connection.execute_wrapper(ql):
            work.footer_contact_improved
        print("### 4. work.footer_contact_improved\n\n")
        ql.render()
```

The results:

### 1. self.workindex.footer_contact

| sql                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | params                                                       | many  | status |    duration | Query № |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------- | :---- | :----- | ----------: | ------: |
| SELECT "people_contact"."id", "people_contact"."title", "people_contact"."text", "people_contact"."cta", "people_contact"."name", "people_contact"."role", "people_contact"."image_id", "people_contact"."default_contact" FROM "people_contact" WHERE "people_contact"."default_contact" ORDER BY "people_contact"."id" ASC LIMIT 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | ()                                                           | False | ok     |  7.5607e-05 |       1 |
| SELECT "wagtailcore_page"."id", "wagtailcore_page"."content_type_id" FROM "wagtailcore_page" WHERE ("wagtailcore_page"."path" IN (%s, %s, %s, %s) AND NOT ("wagtailcore_page"."id" = %s)) ORDER BY "wagtailcore_page"."depth" DESC                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | ('0001', '00010001', '000100010001', '0001000100010002', 91) | False | ok     | 0.000135567 |       2 |
| SELECT "wagtailcore_page"."id", "wagtailcore_page"."path", "wagtailcore_page"."depth", "wagtailcore_page"."numchild", "wagtailcore_page"."translation_key", "wagtailcore_page"."locale_id", "wagtailcore_page"."latest_revision_id", "wagtailcore_page"."live", "wagtailcore_page"."has_unpublished_changes", "wagtailcore_page"."first_published_at", "wagtailcore_page"."last_published_at", "wagtailcore_page"."live_revision_id", "wagtailcore_page"."go_live_at", "wagtailcore_page"."expire_at", "wagtailcore_page"."expired", "wagtailcore_page"."locked", "wagtailcore_page"."locked_at", "wagtailcore_page"."locked_by_id", "wagtailcore_page"."title", "wagtailcore_page"."draft_title", "wagtailcore_page"."slug", "wagtailcore_page"."content_type_id", "wagtailcore_page"."url_path", "wagtailcore_page"."owner_id", "wagtailcore_page"."seo_title", "wagtailcore_page"."show_in_menus", "wagtailcore_page"."search_description", "wagtailcore_page"."latest_revision_created_at", "wagtailcore_page"."alias_of_id", "torchbox_homepage"."page_ptr_id", "torchbox_homepage"."social_image_id", "torchbox_homepage"."social_text", "torchbox_homepage"."theme", "torchbox_homepage"."contact_id", "torchbox_homepage"."hero_intro_primary", "torchbox_homepage"."hero_intro_secondary", "torchbox_homepage"."intro_body", "torchbox_homepage"."work_title", "torchbox_homepage"."blog_title", "torchbox_homepage"."clients_title" FROM "torchbox_homepage" INNER JOIN "wagtailcore_page" ON ("torchbox_homepage"."page_ptr_id" = "wagtailcore_page"."id") WHERE "torchbox_homepage"."page_ptr_id" IN (%s) ORDER BY "wagtailcore_page"."path" ASC | (89,)                                                        | False | ok     | 0.000273931 |       3 |
| SELECT "wagtailcore_page"."id", "wagtailcore_page"."path", "wagtailcore_page"."depth", "wagtailcore_page"."numchild", "wagtailcore_page"."translation_key", "wagtailcore_page"."locale_id", "wagtailcore_page"."latest_revision_id", "wagtailcore_page"."live", "wagtailcore_page"."has_unpublished_changes", "wagtailcore_page"."first_published_at", "wagtailcore_page"."last_published_at", "wagtailcore_page"."live_revision_id", "wagtailcore_page"."go_live_at", "wagtailcore_page"."expire_at", "wagtailcore_page"."expired", "wagtailcore_page"."locked", "wagtailcore_page"."locked_at", "wagtailcore_page"."locked_by_id", "wagtailcore_page"."title", "wagtailcore_page"."draft_title", "wagtailcore_page"."slug", "wagtailcore_page"."content_type_id", "wagtailcore_page"."url_path", "wagtailcore_page"."owner_id", "wagtailcore_page"."seo_title", "wagtailcore_page"."show_in_menus", "wagtailcore_page"."search_description", "wagtailcore_page"."latest_revision_created_at", "wagtailcore_page"."alias_of_id" FROM "wagtailcore_page" WHERE "wagtailcore_page"."id" IN (%s, %s) ORDER BY "wagtailcore_page"."path" ASC                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | (2, 1)                                                       | False | ok     | 0.000169744 |       4 |
| SELECT "people_contact"."id", "people_contact"."title", "people_contact"."text", "people_contact"."cta", "people_contact"."name", "people_contact"."role", "people_contact"."image_id", "people_contact"."default_contact" FROM "people_contact" WHERE "people_contact"."id" = %s LIMIT 21                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | (37,)                                                        | False | ok     | 0.000110811 |       5 |

### 2. self.workindex.footer_contact_improved

| sql                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | params                                                       | many  | status |    duration | Query № |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------- | :---- | :----- | ----------: | ------: |
| SELECT "wagtailcore_page"."id", "wagtailcore_page"."content_type_id" FROM "wagtailcore_page" WHERE ("wagtailcore_page"."path" IN (%s, %s, %s, %s) AND NOT ("wagtailcore_page"."id" = %s)) ORDER BY "wagtailcore_page"."depth" DESC                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | ('0001', '00010001', '000100010001', '0001000100010002', 91) | False | ok     | 0.000138497 |       1 |
| SELECT "wagtailcore_page"."id", "wagtailcore_page"."path", "wagtailcore_page"."depth", "wagtailcore_page"."numchild", "wagtailcore_page"."translation_key", "wagtailcore_page"."locale_id", "wagtailcore_page"."latest_revision_id", "wagtailcore_page"."live", "wagtailcore_page"."has_unpublished_changes", "wagtailcore_page"."first_published_at", "wagtailcore_page"."last_published_at", "wagtailcore_page"."live_revision_id", "wagtailcore_page"."go_live_at", "wagtailcore_page"."expire_at", "wagtailcore_page"."expired", "wagtailcore_page"."locked", "wagtailcore_page"."locked_at", "wagtailcore_page"."locked_by_id", "wagtailcore_page"."title", "wagtailcore_page"."draft_title", "wagtailcore_page"."slug", "wagtailcore_page"."content_type_id", "wagtailcore_page"."url_path", "wagtailcore_page"."owner_id", "wagtailcore_page"."seo_title", "wagtailcore_page"."show_in_menus", "wagtailcore_page"."search_description", "wagtailcore_page"."latest_revision_created_at", "wagtailcore_page"."alias_of_id", "torchbox_homepage"."page_ptr_id", "torchbox_homepage"."social_image_id", "torchbox_homepage"."social_text", "torchbox_homepage"."theme", "torchbox_homepage"."contact_id", "torchbox_homepage"."hero_intro_primary", "torchbox_homepage"."hero_intro_secondary", "torchbox_homepage"."intro_body", "torchbox_homepage"."work_title", "torchbox_homepage"."blog_title", "torchbox_homepage"."clients_title" FROM "torchbox_homepage" INNER JOIN "wagtailcore_page" ON ("torchbox_homepage"."page_ptr_id" = "wagtailcore_page"."id") WHERE "torchbox_homepage"."page_ptr_id" IN (%s) ORDER BY "wagtailcore_page"."path" ASC | (89,)                                                        | False | ok     | 0.000252826 |       2 |
| SELECT "wagtailcore_page"."id", "wagtailcore_page"."path", "wagtailcore_page"."depth", "wagtailcore_page"."numchild", "wagtailcore_page"."translation_key", "wagtailcore_page"."locale_id", "wagtailcore_page"."latest_revision_id", "wagtailcore_page"."live", "wagtailcore_page"."has_unpublished_changes", "wagtailcore_page"."first_published_at", "wagtailcore_page"."last_published_at", "wagtailcore_page"."live_revision_id", "wagtailcore_page"."go_live_at", "wagtailcore_page"."expire_at", "wagtailcore_page"."expired", "wagtailcore_page"."locked", "wagtailcore_page"."locked_at", "wagtailcore_page"."locked_by_id", "wagtailcore_page"."title", "wagtailcore_page"."draft_title", "wagtailcore_page"."slug", "wagtailcore_page"."content_type_id", "wagtailcore_page"."url_path", "wagtailcore_page"."owner_id", "wagtailcore_page"."seo_title", "wagtailcore_page"."show_in_menus", "wagtailcore_page"."search_description", "wagtailcore_page"."latest_revision_created_at", "wagtailcore_page"."alias_of_id" FROM "wagtailcore_page" WHERE "wagtailcore_page"."id" IN (%s, %s) ORDER BY "wagtailcore_page"."path" ASC                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | (2, 1)                                                       | False | ok     | 0.000171783 |       3 |
| SELECT "people_contact"."id", "people_contact"."title", "people_contact"."text", "people_contact"."cta", "people_contact"."name", "people_contact"."role", "people_contact"."image_id", "people_contact"."default_contact" FROM "people_contact" WHERE "people_contact"."id" = %s LIMIT 21                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | (37,)                                                        | False | ok     | 0.000108416 |       4 |

### 3. work.footer_contact

0 queries

### 4. work.footer_contact_improved

0 queries
