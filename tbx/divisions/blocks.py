from tbx.core.blocks import (
    FeaturedServicesBlock,
    FourPhotoCollageBlock,
    IntroductionWithImagesBlock,
    NumericStatisticsGroupBlock,
    PartnersBlock,
    StoryBlock,
    TextualStatisticsGroupBlock,
)


class DivisionStoryBlock(StoryBlock):
    four_photo_collage = FourPhotoCollageBlock()
    introduction_with_images = IntroductionWithImagesBlock()
    numeric_statistics = NumericStatisticsGroupBlock()
    textual_statistics = TextualStatisticsGroupBlock()
    partners_block = PartnersBlock()
    featured_services = FeaturedServicesBlock()
