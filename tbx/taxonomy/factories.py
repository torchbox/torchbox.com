from django.utils.text import slugify

import factory
from factory.django import DjangoModelFactory
from tbx.taxonomy.models import Sector, Service, Team


class ServiceFactory(DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=20)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    description = factory.Faker("paragraph")
    sort_order = factory.Sequence(lambda n: n)

    class Meta:
        model = Service


class SectorFactory(DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=20)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    description = factory.Faker("paragraph")
    sort_order = factory.Sequence(lambda n: n)

    class Meta:
        model = Sector


class TeamFactory(DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=20)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    description = factory.Faker("paragraph")
    sort_order = factory.Sequence(lambda n: n)

    class Meta:
        model = Team
