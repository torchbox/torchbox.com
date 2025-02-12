# Generated by Django 5.1.4 on 2025-01-28 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("divisions", "0002_divisionmixin_and_navigationsetmixin"),
        ("navigation", "0007_divisionmixin_and_navigationsetmixin"),
        (
            "torchbox",
            "0039_remove_homepage_introduction_homepage_hero_heading_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="override_navigation_set",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="navigation.navigationset",
            ),
        ),
        migrations.AddField(
            model_name="standardpage",
            name="division",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="divisions.divisionpage",
            ),
        ),
        migrations.AddField(
            model_name="standardpage",
            name="override_navigation_set",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="navigation.navigationset",
            ),
        ),
    ]
