# Generated by Django 4.2.9 on 2024-02-06 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0004_personindexpage_theme_personpage_theme"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ContactReason",
        ),
        migrations.DeleteModel(
            name="ContactReasonsList",
        ),
    ]
