# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0010_divisionmixin_and_navigationsetmixin"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="eventindexpage",
            name="override_navigation_set",
        ),
    ]
