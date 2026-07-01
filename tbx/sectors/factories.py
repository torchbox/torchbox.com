from wagtail import blocks

import factory
import wagtail_factories

from tbx.core.blocks import DynamicHeroBlock
from tbx.core.factories import DynamicHeroBlockFactory, StoryBlockFactory

from .models import SectorsIndexPage


class SectorsIndexHeroStreamBlock(blocks.StreamBlock):
    hero = DynamicHeroBlock()


class SectorsIndexHeroStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    class Meta:
        model = SectorsIndexHeroStreamBlock

    hero = factory.SubFactory(DynamicHeroBlockFactory)


class SectorsIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = SectorsIndexPage

    title = "Sectors"

    @factory.post_generation
    def hero(obj, create, extracted, **kwargs):
        blocks = kwargs or {"0": "hero"}
        obj.hero = SectorsIndexHeroStreamBlockFactory(**blocks)

    @factory.post_generation
    def body(obj, create, extracted, **kwargs):
        blocks = kwargs or {"0": "paragraph"}
        obj.body = StoryBlockFactory(**blocks)
