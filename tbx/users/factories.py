from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

import factory


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.LazyFunction(lambda: make_password("password"))
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = get_user_model()
