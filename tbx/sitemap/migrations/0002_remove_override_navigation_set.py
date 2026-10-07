# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sitemap", "0001_initial"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sitemappage",
            name="override_navigation_set",
        ),
    ]
