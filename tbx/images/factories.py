from wagtail_factories import ImageFactory

from tbx.images.models import CustomImage


class CustomImageFactory(ImageFactory):
    class Meta:
        model = CustomImage
