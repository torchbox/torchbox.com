# Generated by Django 4.2.8 on 2024-01-11 14:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("torchbox", "0004_alter_standardpage_body"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="advert",
            name="page",
        ),
        migrations.RemoveField(
            model_name="advertplacement",
            name="advert",
        ),
        migrations.RemoveField(
            model_name="advertplacement",
            name="page",
        ),
        migrations.DeleteModel(
            name="ParticleSnippet",
        ),
        migrations.DeleteModel(
            name="Advert",
        ),
        migrations.DeleteModel(
            name="AdvertPlacement",
        ),
    ]
