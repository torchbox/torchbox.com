import factory
from factory.django import DjangoModelFactory

from tbx.navigation.models import NavigationSet


class NavigationSetFactory(DjangoModelFactory):
    class Meta:
        model = NavigationSet

    name = factory.Faker("text", max_nb_chars=20)
