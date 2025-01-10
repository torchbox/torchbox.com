import factory
import wagtail_factories
from tbx.core.factories import StoryBlockFactory

from .models import ServiceAreaPage, ServicePage


class ServicePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ServicePage

    title = factory.Faker("text", max_nb_chars=100)

    @factory.post_generation
    def body(obj, create, extracted, **kwargs):
        blocks = kwargs or {"0": "paragraph"}
        obj.body = StoryBlockFactory(**blocks)


class ServiceAreaPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ServiceAreaPage

    title = factory.Faker("text", max_nb_chars=100)
    subtitle = factory.Faker("text", max_nb_chars=100)

    @factory.post_generation
    def body(obj, create, extracted, **kwargs):
        blocks = kwargs or {"0": "paragraph"}
        obj.body = StoryBlockFactory(**blocks)
