# Generated by Django 4.2.9 on 2024-03-15 09:04

from django.db import migrations

import tbx.core.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        (
            "navigation",
            "0005_navigationsettings_primary_navigation_child_display_behaviour",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="navigationsettings",
            name="footer_links",
            field=tbx.core.utils.fields.StreamField(
                blank=True,
                help_text="Single list of elements at the base of the page.",
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="navigationsettings",
            name="footer_logos",
            field=tbx.core.utils.fields.StreamField(
                blank=True,
                help_text="Single list of logos that appear before the footer box",
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="navigationsettings",
            name="primary_navigation",
            field=tbx.core.utils.fields.StreamField(
                blank=True, help_text="Main site navigation", use_json_field=True
            ),
        ),
    ]
