# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
        ("torchbox", "0043_remove_override_navigation_set"),
        ("divisions", "0004_remove_override_navigation_set"),
        ("blog", "0030_remove_override_navigation_set"),
        ("services", "0026_remove_override_navigation_set"),
        ("work", "0038_remove_override_navigation_set"),
        ("people", "0013_remove_override_navigation_set"),
        ("events", "0011_remove_override_navigation_set"),
        ("impact_reports", "0008_remove_override_navigation_set"),
        ("sitemap", "0002_remove_override_navigation_set"),
    ]

    operations = [
        migrations.DeleteModel(
            name="NavigationSet",
        ),
    ]
