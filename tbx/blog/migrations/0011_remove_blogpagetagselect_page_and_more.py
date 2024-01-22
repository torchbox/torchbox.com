# Generated by Django 4.2.9 on 2024-01-22 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0010_add_help_text_to_alt_text_field_in_image_block"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="blogpagetagselect",
            name="page",
        ),
        migrations.RemoveField(
            model_name="blogpagetagselect",
            name="tag",
        ),
        migrations.RemoveField(
            model_name="blogindexpage",
            name="intro",
        ),
        migrations.DeleteModel(
            name="BlogIndexPageRelatedLink",
        ),
        migrations.DeleteModel(
            name="BlogPageTagSelect",
        ),
    ]