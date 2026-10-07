# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0029_relatedblogpage"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="blogindexpage",
            name="override_navigation_set",
        ),
        migrations.RemoveField(
            model_name="blogpage",
            name="override_navigation_set",
        ),
    ]
