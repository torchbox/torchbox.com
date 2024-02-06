from django.utils.text import slugify

import factory
from factory.django import DjangoModelFactory
from tbx.taxonomy.models import Service


class ServiceFactory(DjangoModelFactory):
    """
    Factory for generating Service instances

    *Usage*:

    Create a Service instance
    `service_instance = ServiceFactory()`
    """

    name = factory.Faker("text", max_nb_chars=20)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    description = factory.Faker("paragraph")
    sort_order = factory.Sequence(lambda n: n)

    class Meta:
        model = Service
