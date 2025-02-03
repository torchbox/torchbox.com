# Generated by Django 4.2.9 on 2024-02-19 14:46

from django.db import migrations

import modelcluster.fields


class Migration(migrations.Migration):
    dependencies = [
        ("taxonomy", "0002_sector_team_remove_service_contact_reasons_and_more"),
        ("blog", "0019_add_contact_mixin_to_all_page_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogpage",
            name="related_sectors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, related_name="blog_posts", to="taxonomy.sector"
            ),
        ),
    ]
