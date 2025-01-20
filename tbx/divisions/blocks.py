from tbx.core.blocks import (
    FeaturedServicesBlock,
    FourPhotoCollageBlock,
    IntroductionWithImagesBlock,
    NumericStatisticsGroupBlock,
    PartnersBlock,
    StoryBlock,
)


class DivisionStoryBlock(StoryBlock):
    four_photo_collage = FourPhotoCollageBlock()
    introduction_with_images = IntroductionWithImagesBlock()
    numeric_statistics = NumericStatisticsGroupBlock()
    partners_block = PartnersBlock()
    featured_services = FeaturedServicesBlock()
