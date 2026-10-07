from tbx.core.blocks import (
    FeaturedServicesBlock,
    FourPhotoCollageBlock,
    IconKeyPointsBlock,
    IntroductionWithImagesBlock,
    LinkColumnsBlock,
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
    key_points = IconKeyPointsBlock(label="Key points with icons")
    partners_block = PartnersBlock()
    featured_services = FeaturedServicesBlock()
    link_columns = LinkColumnsBlock()
