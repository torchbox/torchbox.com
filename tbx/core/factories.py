from wagtail.blocks import RichTextBlock

import factory
import wagtail_factories

from tbx.core.blocks import StoryBlock
from tbx.core.models import HomePage, StandardPage


class RichTextBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = RichTextBlock


class StoryBlockFactory(wagtail_factories.StreamBlockFactory):
    h2 = factory.Faker("text", max_nb_chars=100)
    h3 = factory.Faker("text", max_nb_chars=100)
    h4 = factory.Faker("text", max_nb_chars=100)
    intro = factory.SubFactory(RichTextBlockFactory)
    paragraph = factory.SubFactory(RichTextBlockFactory)

    class Meta:
        model = StoryBlock


class HomePageFactory(wagtail_factories.PageFactory):
    title = "Home"

    class Meta:
        model = HomePage


class StandardPageFactory(wagtail_factories.PageFactory):
    title = factory.Faker("text", max_nb_chars=100)
    body = StoryBlockFactory()

    class Meta:
        model = StandardPage
