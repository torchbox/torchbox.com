# Generated by Django 4.2.9 on 2024-03-15 10:52

from django.db import migrations

import tbx.core.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("torchbox", "0030_remove_featured_case_study_tagline"),
        ("torchbox", "0030_use_custom_streamfield"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="body",
            field=tbx.core.utils.fields.StreamField(use_json_field=True),
        ),
    ]
