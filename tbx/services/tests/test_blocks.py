from django.test import SimpleTestCase

from wagtail.blocks import StructBlockValidationError

from tbx.services.blocks import OptionalLinkPromoBlock, PromoBlock


class OptionalLinkPromoBlockTestCase(SimpleTestCase):
    def test_basic_promo_block_button_link_required(self):
        try:
            PromoBlock().clean({"button_link": []})
        except StructBlockValidationError:
            pass
        else:
            self.fail("PromoBlock.button_link should be required")

    def test_custom_promo_block_button_link_optional(self):
        try:
            OptionalLinkPromoBlock().clean({"button_link": []})
        except StructBlockValidationError as e:
            self.fail(e.as_json_data())

    def test_basic_promo_block_button_text_required(self):
        try:
            PromoBlock().clean({"button_text": ""})
        except StructBlockValidationError:
            pass
        else:
            self.fail("PromoBlock.button_text should be required")

    def test_custom_promo_block_button_text_optional(self):
        try:
            OptionalLinkPromoBlock().clean({"button_text": ""})
        except StructBlockValidationError as e:
            self.fail(e.as_json_data())

    def test_custom_promo_block_link_required_if_text_provided(self):
        try:
            OptionalLinkPromoBlock().clean({"button_text": "test", "button_link": []})
        except StructBlockValidationError:
            pass
        else:
            self.fail(
                "PromoBlock.button_link should be required if button_text is provided"
            )
