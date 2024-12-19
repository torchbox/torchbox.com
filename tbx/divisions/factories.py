import factory
import wagtail_factories
from tbx.core.blocks import DynamicHeroBlock
from tbx.core.factories import DynamicHeroBlockFactory, StoryBlockFactory
from wagtail import blocks

from .models import DivisionPage


class DynamicHeroStreamBlock(blocks.StreamBlock):
    hero = DynamicHeroBlock()


class DynamicHeroStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    class Meta:
        model = DynamicHeroStreamBlock

    hero = factory.SubFactory(DynamicHeroBlockFactory)


class DivisionPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = DivisionPage

    title = "Charity"
    label = "Charity"

    @factory.post_generation
    def hero(obj, create, extracted, **kwargs):
        blocks = kwargs or {"0": "hero"}
        obj.hero = DynamicHeroStreamBlockFactory(**blocks)

    @factory.post_generation
    def body(obj, create, extracted, **kwargs):
        blocks = kwargs or {"0": "paragraph"}
        obj.body = StoryBlockFactory(**blocks)