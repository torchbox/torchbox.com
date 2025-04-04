# Generated by Django 4.2.9 on 2024-03-18 06:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("work", "0029_use_custom_streamfield"),
    ]

    operations = [
        migrations.AddField(
            model_name="workpage",
            name="remove_desaturation_on_header_image",
            field=models.BooleanField(
                default=False,
                help_text="Do not apply a desaturation filter to the image.",
                verbose_name="Remove desaturation filter",
            ),
        ),
    ]
