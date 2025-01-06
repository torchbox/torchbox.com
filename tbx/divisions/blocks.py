from tbx.core.blocks import (
    FeaturedServicesBlock,
    FourPhotoCollageBlock,
    IntroductionWithImagesBlock,
    PartnersBlock,
    StoryBlock,
)


class DivisionStoryBlock(StoryBlock):
    four_photo_collage = FourPhotoCollageBlock()
    introduction_with_images = IntroductionWithImagesBlock()
    partners_block = PartnersBlock()
    featured_services = FeaturedServicesBlock()
