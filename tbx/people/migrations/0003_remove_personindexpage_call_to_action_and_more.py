# Generated by Django 4.2.8 on 2024-01-11 10:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0002_remove_culturepagekeypoint_linked_page_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="personindexpage",
            name="call_to_action",
        ),
        migrations.RemoveField(
            model_name="personpage",
            name="call_to_action",
        ),
    ]
