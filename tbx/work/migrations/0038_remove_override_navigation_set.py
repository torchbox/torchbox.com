# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("work", "0037_divisionmixin_and_navigationsetmixin"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalworkpage",
            name="override_navigation_set",
        ),
        migrations.RemoveField(
            model_name="workindexpage",
            name="override_navigation_set",
        ),
        migrations.RemoveField(
            model_name="workpage",
            name="override_navigation_set",
        ),
    ]
