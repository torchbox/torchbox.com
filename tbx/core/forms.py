from django.conf import settings
from django.forms import Form, fields


class ModeSwitcherForm(Form):
    switch_mode = fields.ChoiceField(
        choices=[(mode, mode) for mode in settings.ALLOWED_MODES]
    )
    next_url = fields.CharField(required=False)
