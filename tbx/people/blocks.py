from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class InstagramEmbedBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    link = blocks.URLBlock(
        required=False,
        help_text="Link to a specific post here or leave blank for it to link to https://www.instagram.com/torchboxltd/",
    )

    class Meta:
        icon = "group"
