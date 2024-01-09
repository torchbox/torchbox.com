# Generated by Django 4.2.8 on 2024-01-04 07:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="culturepagekeypoint",
            name="linked_page",
        ),
        migrations.RemoveField(
            model_name="culturepagekeypoint",
            name="page",
        ),
        migrations.RemoveField(
            model_name="culturepagelink",
            name="link",
        ),
        migrations.RemoveField(
            model_name="culturepagelink",
            name="page",
        ),
        migrations.RemoveField(
            model_name="valuespage",
            name="page_ptr",
        ),
        migrations.RemoveField(
            model_name="valuespage",
            name="social_image",
        ),
        migrations.RemoveField(
            model_name="valuespagevalue",
            name="page",
        ),
        migrations.RemoveField(
            model_name="valuespagevalue",
            name="value_image",
        ),
        migrations.DeleteModel(
            name="CulturePage",
        ),
        migrations.DeleteModel(
            name="CulturePageKeyPoint",
        ),
        migrations.DeleteModel(
            name="CulturePageLink",
        ),
        migrations.DeleteModel(
            name="ValuesPage",
        ),
        migrations.DeleteModel(
            name="ValuesPageValue",
        ),
    ]