from wagtail import blocks

import factory
from faker import Faker
import wagtail_factories

from tbx.core.blocks import DynamicHeroBlock, StoryBlock
from tbx.core.models import HomePage, StandardPage


fake = Faker()


class DynamicHeroBlockFactory(wagtail_factories.StructBlockFactory):
    class Meta:
        model = DynamicHeroBlock

    static_text = fake.sentence()

    @factory.post_generation
    def dynamic_text(obj, create, extracted, **kwargs):
        values = extracted or fake.sentences(nb=5)
        obj["dynamic_text"] = blocks.list_block.ListValue(
            blocks.ListBlock(blocks.CharBlock()), values
        )


class RichTextBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.RichTextBlock


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
    hero_heading_1 = "The digital partner"
    hero_heading_2 = "for positive change"

    class Meta:
        model = HomePage


class StandardPageFactory(wagtail_factories.PageFactory):
    title = factory.Faker("text", max_nb_chars=100)
    body = StoryBlockFactory()

    class Meta:
        model = StandardPage
