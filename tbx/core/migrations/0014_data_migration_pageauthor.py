# Generated by Django 4.2.9 on 2024-01-25 08:45

from django.db import migrations, models
import django.db.models.deletion

import modelcluster.fields


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0003_remove_personindexpage_call_to_action_and_more"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("torchbox", "0013_add_help_text_to_alt_text_field_in_image_block"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageAuthor",
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
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="people.author",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="authors",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
