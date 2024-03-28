from tbx.core.blocks import BaseEventBlock
from wagtail.images.blocks import ImageChooserBlock


class EventItemBlock(BaseEventBlock):
    image = ImageChooserBlock(required=False)
