# Generated by Django 4.2.9 on 2024-02-12 22:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0005_add_contact_mixin_to_all_page_models"),
        ("blog", "0017_blogindexpage_theme_blogpage_theme"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogindexpage",
            name="contact",
            field=models.ForeignKey(
                blank=True,
                help_text="The contact will be applied to this page's footer and all of its descendants.\nIf no contact is selected, it will be derived from this page's ancestors, eventually falling back to the default contact.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="people.contact",
            ),
        ),
        migrations.AddField(
            model_name="blogpage",
            name="contact",
            field=models.ForeignKey(
                blank=True,
                help_text="The contact will be applied to this page's footer and all of its descendants.\nIf no contact is selected, it will be derived from this page's ancestors, eventually falling back to the default contact.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="people.contact",
            ),
        ),
    ]
