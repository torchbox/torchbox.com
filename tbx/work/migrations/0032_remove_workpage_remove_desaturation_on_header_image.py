# Generated by Django 4.2.11 on 2024-04-09 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("work", "0031_rename_feed_image_historicalworkpage_header_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="workpage",
            name="remove_desaturation_on_header_image",
        ),
    ]
