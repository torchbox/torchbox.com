from tbx.core.blocks import (
    FeaturedServicesBlock,
    FourPhotoCollageBlock,
    IntroductionWithImagesBlock,
    LinkColumnsBlock,
    NumericStatisticsGroupBlock,
    PartnersBlock,
    StoryBlock,
    TextualStatisticsGroupBlock,
)


class SectorsIndexStoryBlock(StoryBlock):
    """
    StreamBlock used by SectorsIndexPage.

    Currently identical to tbx.divisions.blocks.DivisionStoryBlock — the
    two are deliberately kept as separate classes so the sector index
    can diverge independently as IA evolves.
    """

    four_photo_collage = FourPhotoCollageBlock()
    introduction_with_images = IntroductionWithImagesBlock()
    numeric_statistics = NumericStatisticsGroupBlock()
    textual_statistics = TextualStatisticsGroupBlock()
    partners_block = PartnersBlock()
    featured_services = FeaturedServicesBlock()
    link_columns = LinkColumnsBlock()
