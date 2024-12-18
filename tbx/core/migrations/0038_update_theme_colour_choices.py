# Generated by Django 4.2.16 on 2024-12-09 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("torchbox", "0037_merge_20240725_1000"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="theme",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "None"),
                    ("theme-coral", "Coral"),
                    ("theme-nebuline", "Nebuline"),
                    ("theme-lagoon", "Lagoon"),
                    ("theme-green", "Green"),
                ],
                max_length=25,
            ),
        ),
        migrations.AlterField(
            model_name="standardpage",
            name="theme",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "None"),
                    ("theme-coral", "Coral"),
                    ("theme-nebuline", "Nebuline"),
                    ("theme-lagoon", "Lagoon"),
                    ("theme-green", "Green"),
                ],
                max_length=25,
            ),
        ),
    ]
