from django.core.exceptions import ValidationError

from wagtail.admin.forms import WagtailAdminModelForm


class ContactAdminForm(WagtailAdminModelForm):
    def clean(self):
        cleaned_data = super().clean()

        # These fields are needed in order to avoid potential missing info
        # when the contact is rendered in the site-wide footer
        key_fields = ["title", "text", "cta", "name", "role", "image"]

        for field_name in key_fields:
            field_value = cleaned_data.get(field_name)
            if not field_value:
                self.add_error(
                    field_name,
                    ValidationError(
                        (f"Please specify the {field_name}."),
                        code="invalid",
                    ),
                )

        return cleaned_data
