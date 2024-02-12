from wagtail import blocks


class ContactCTAStructValue(blocks.StructValue):
    @property
    def url(self):
        """
        return an href-ready value for `button_link`
        """
        block = self.get("button_link")[0]
        if (block_type := block.block_type) == "internal_link":
            # Ensure page exists and is live.
            if block.value and block.value.live:
                return block.value.url
        elif block_type == "external_link":
            return block.value
        elif block_type == "email":
            return f"mailto:{block.value}"

        return ""


class ContactCTABlock(blocks.StructBlock):
    button_text = blocks.CharBlock(max_length=55)
    button_link = blocks.StreamBlock(
        [
            ("internal_link", blocks.PageChooserBlock()),
            ("external_link", blocks.URLBlock()),
            ("email", blocks.EmailBlock()),
        ],
        required=True,
        max_num=1,
    )

    class Meta:
        value_class = ContactCTAStructValue
