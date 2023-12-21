# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-17 09:55


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("torchbox", "0019_googleadgrantspage_to_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="googleadgrantspage",
            name="call_to_action_embed_url",
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name="googleadgrantspage",
            name="call_to_action_title",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
