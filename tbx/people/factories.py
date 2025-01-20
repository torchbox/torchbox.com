import json
import logging

import factory
from factory.django import DjangoModelFactory
from faker import Faker
import wagtail_factories

from tbx.core.factories import StandardPageFactory
from tbx.core.models import HomePage
from tbx.images.factories import CustomImageFactory
from tbx.people.models import (
    Author,
    Contact,
    ContactReason,
    ContactReasonsList,
    PersonIndexPage,
    PersonPage,
)
from tbx.taxonomy.factories import TeamFactory
from tbx.taxonomy.models import Team


faker = Faker(["en_GB"])
logger = logging.getLogger(__name__)


def get_button_link_value(link_type, faker, page=None):
    """
    Helper function for generating a `button_link` value based on the `link_type`.

    This is used by the ContactFactory to generate a random `button_link` value
    for the `cta` StreamField.

    Args:
        link_type (str): The type of link to generate
        (`"internal_link"`, `"external_link"`, or `"email"`).
        faker (Faker): A Faker instance to use for generating random values.
        page (Page): (Optional) A Wagtail Page instance to use as the link target.
    """
    if link_type == "internal_link":
        if page:
            return page.pk
        else:
            if home := HomePage.objects.first():
                return home.pk
            else:
                return StandardPageFactory().pk
    elif link_type == "external_link":
        return faker.url()
    elif link_type == "email":
        return faker.email()


class ContactFactory(DjangoModelFactory):
    """
    Factory for creating Contact instances with various call to action (CTA) types.

    Usage:
        To create a Contact instance with a specific CTA type,
        use the `cta` argument with values specified as a dict, like this:

        Examples:
            ContactFactory(cta={"link_type": "external_link"})
            ContactFactory(cta={"link_type": "email"})
            ContactFactory(cta={"link_type": "internal_link"})
            ContactFactory(cta={"link_type": "internal_link", "page": <Page instance>})

        Calling the factory without providing any arguments will create a Contact
        instance without a CTA

        Example:
            ContactFactory()
    """

    title = factory.Faker("text", max_nb_chars=25)
    text = factory.Faker("text", max_nb_chars=100)

    name = factory.Faker("name")
    role = factory.Faker("job")
    image = factory.SubFactory(CustomImageFactory)

    @factory.post_generation
    def cta(obj, create, extracted, **kwargs):
        if not create or not extracted:
            return

        if not isinstance(extracted, dict):
            raise ValueError(
                "`cta` value must be provided as a dictionary with acceptable keys: `link_type` and `page`.\n"
                "Examples:\n\n"
                "ContactFactory(cta={'link_type': 'external_link'})\n"
                "ContactFactory(cta={'link_type': 'email'})\n"
                "ContactFactory(cta={'link_type': 'internal_link'})\n"
                "ContactFactory(cta={'link_type': 'internal_link', 'page': <Page instance>})"
            )

        if extracted:
            link_type = extracted.get("link_type", "external_link")
            page = extracted.get("page", None)

            acceptable_link_types = ["internal_link", "external_link", "email"]
            if link_type not in acceptable_link_types:
                raise ValueError(
                    f"Invalid link type: {link_type}\n"
                    "Acceptable link types are: {}".format(
                        ", ".join(acceptable_link_types)
                    )
                )
            if page and link_type != "internal_link":
                logger.warning(
                    "Page argument ignored because link type is not 'internal_link'"
                )

            cta_value = {
                "type": "call_to_action",
                "value": {
                    "button_link": [
                        {
                            "type": link_type,
                            "value": get_button_link_value(link_type, faker, page),
                        }
                    ],
                    "button_text": faker.text(max_nb_chars=55),
                },
            }

            obj.cta = json.dumps([cta_value])
            obj.save()

    class Meta:
        model = Contact


class ContactReasonFactory(DjangoModelFactory):
    """
    Factory for generating ContactReason instances.
    Note that this factory cannot be instantiated on its own because ContactReason
    requires a parent ContactReasonsList instance to be associated with.
    Use the ContactReasonsListFactory to create ContactReason instances
    with related parents.
    """

    title = factory.Faker("text", max_nb_chars=20)
    description = factory.Faker("sentence")

    class Meta:
        model = ContactReason


class ContactReasonsListFactory(DjangoModelFactory):
    """
    Factory for generating ContactReasonsList instances along with
    related ContactReason instances.

    *Usage*:

    1. Create a ContactReasonsList instance without related reasons:

    ```
    contact_reasons_list = ContactReasonsListFactory()
    ```

    2. Create a ContactReasonsList instance with a specific number of
    related ContactReason instances:

    ```
    contact_reasons_list_with_reasons = ContactReasonsListFactory(reasons=3)
    ```
    """

    name = factory.Faker("text", max_nb_chars=20)
    heading = factory.Faker("text", max_nb_chars=30)

    class Meta:
        model = ContactReasonsList

    @factory.post_generation
    def reasons(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            if isinstance(extracted, int):
                ContactReasonFactory.create_batch(extracted, page=self)
            else:
                raise ValueError("The 'reasons' field expects an integer value.")


class AuthorFactory(DjangoModelFactory):
    name = factory.Faker("name")
    role = factory.Faker("job")
    image = factory.SubFactory(CustomImageFactory)

    class Meta:
        model = Author


class PersonIndexPageFactory(wagtail_factories.PageFactory):
    title = factory.Faker("text", max_nb_chars=12)
    strapline = factory.Faker("text", max_nb_chars=100)

    class Meta:
        model = PersonIndexPage


class PersonPageFactory(wagtail_factories.PageFactory):
    """
    Factory for generating `PersonPage` instances.
    By default, this factory will create a PersonPage instance with a related team.

    You can optionally either specify the name of the related team or a
    `tbx.taxonomy.models.Team` instance. Please see below for some examples.


    **Usage examples**

    1. Create a PersonPage instance with a random related team:

    ```
    >>> person = PersonPageFactory()
    >>> person.related_teams.all()
    <QuerySet [<Team: Spend can white.>]>
    ```

    2. Create a PersonPage instance with a specific related team:

    ```
    >>> team = TeamFactory(name="Foo")
    >>> person = PersonPageFactory(related_teams=team)
    >>> person.related_teams.all()
    <QuerySet [<Team: Foo>]>
    ```

    3. Create a PersonPage instance specifying the name of the related team:

    ```
    >>> person = PersonPageFactory(related_teams="Foo Bar")
    >>> person.related_teams.all()
    <QuerySet [<Team: Foo Bar>]>
    ```
    """

    title = factory.Faker("name")
    role = factory.Faker("job")
    biography = f"<p>{faker.paragraph()}</p>"
    image = factory.SubFactory(CustomImageFactory)

    @factory.post_generation
    def related_teams(self, create, extracted, **kwargs):
        if not create:
            return
        if not extracted:
            self.related_teams.add(TeamFactory())
        if extracted:
            if isinstance(extracted, str):
                self.related_teams.add(TeamFactory(name=extracted))
            elif isinstance(extracted, Team):
                self.related_teams.add(extracted)
            else:
                raise ValueError(
                    "`related_teams` value must either be a string or a `Team` instance."
                )

    class Meta:
        model = PersonPage
