import factory
import wagtail_factories
from tbx.core.factories import RichTextBlockFactory, StoryBlockFactory
from tbx.images.factories import CustomImageFactory
from tbx.taxonomy.factories import ServiceFactory
from tbx.work.models import HistoricalWorkPage, WorkIndexPage, WorkPage


class WorkIndexPageFactory(wagtail_factories.PageFactory):
    title = factory.Faker("text", max_nb_chars=100)
    intro = factory.SubFactory(RichTextBlockFactory)

    class Meta:
        model = WorkIndexPage


class HistoricalWorkPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = HistoricalWorkPage

    title = factory.Faker("text", max_nb_chars=100)
    date = factory.Faker("date_this_year")
    body = StoryBlockFactory()
    feed_image = factory.SubFactory(CustomImageFactory)

    @factory.post_generation
    def related_services(self, create, extracted, **kwargs):
        if not create or not extracted:
            service = ServiceFactory()
            self.related_services.add(service)

        if extracted:
            # Add the iterable of related_services using bulk addition
            self.related_services.add(*extracted)


class WorkPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = WorkPage

    title = factory.Faker("text", max_nb_chars=100)
    date = factory.Faker("date_this_year")
    body = StoryBlockFactory()
    header_image = factory.SubFactory(CustomImageFactory)
    client = factory.Faker("company")
    logo = factory.SubFactory(CustomImageFactory)

    @factory.post_generation
    def related_services(self, create, extracted, **kwargs):
        if not create or not extracted:
            service = ServiceFactory()
            self.related_services.add(service)

        if extracted:
            # Add the iterable of related_services using bulk addition
            self.related_services.add(*extracted)
