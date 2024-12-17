from wagtail.images.blocks import ImageChooserBlock

from tbx.core.blocks import BaseEventBlock


class EventItemBlock(BaseEventBlock):
    image = ImageChooserBlock(required=False)
