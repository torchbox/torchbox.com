# Generated by Django 4.2.9 on 2024-02-29 20:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("work", "0027_add_wide_image_block"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalworkpage",
            name="homepage_image",
        ),
        migrations.DeleteModel(
            name="HistoricalWorkPageScreenshot",
        ),
    ]
