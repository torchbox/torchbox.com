# Generated by Django 4.2.9 on 2024-03-11 19:43

from django.db import migrations

import tbx.core.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0006_add_contact_mixin_to_all_page_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="cta",
            field=tbx.core.utils.fields.StreamField(blank=True, use_json_field=True),
        ),
    ]
