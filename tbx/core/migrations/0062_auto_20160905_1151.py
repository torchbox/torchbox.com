# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-05 10:51


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("torchbox", "0061_auto_20160902_1609"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogindexpage",
            name="intro",
            field=models.TextField(blank=True),
        ),
    ]
