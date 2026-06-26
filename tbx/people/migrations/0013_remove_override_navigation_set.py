# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0012_divisionmixin_and_navigationsetmixin"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="personindexpage",
            name="override_navigation_set",
        ),
        migrations.RemoveField(
            model_name="personpage",
            name="override_navigation_set",
        ),
    ]
