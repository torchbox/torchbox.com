# Generated by Django 5.1.4 on 2025-01-28 09:34

from django.db import migrations, models

import tbx.core.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("navigation", "0006_use_custom_streamfield"),
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.CreateModel(
            name="NavigationSet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("navigation", tbx.core.utils.fields.StreamField(block_lookup={})),
                (
                    "latest_revision",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.revision",
                        verbose_name="latest revision",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
