import factory
import wagtail_factories
from tbx.blog.models import BlogIndexPage, BlogPage
from tbx.core.factories import StoryBlockFactory


class BlogIndexPageFactory(wagtail_factories.PageFactory):
    title = factory.Faker("text", max_nb_chars=100)

    class Meta:
        model = BlogIndexPage


class BlogPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogPage

    title = factory.Faker("text", max_nb_chars=100)
    date = factory.Faker("date_this_year", after_today=True)
    body = StoryBlockFactory()

    @factory.post_generation
    def related_services(self, create, extracted, **kwargs):
        # If a blogpost is created without a service, do not add one
        if not extracted:
            return

        if extracted:
            # Add the iterable of related_services using bulk addition
            self.related_services.add(*extracted)

    @factory.post_generation
    def related_sectors(self, create, extracted, **kwargs):
        # If a blogpost is created without a sector, do not add one
        if not extracted:
            return

        if extracted:
            # Add the iterable of related_services using bulk addition
            self.related_sectors.add(*extracted)
