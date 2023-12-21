# Generated by Django 2.1.5 on 2019-03-16 16:41

from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0012_auto_20190316_1641"),
        ("services", "0023_key_points_heading_not_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicepage",
            name="contact_reasons",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="people.ContactReasonsList",
            ),
        ),
        migrations.AlterField(
            model_name="servicepage",
            name="heading_for_key_points",
            field=wagtail.fields.RichTextField(),
        ),
    ]
