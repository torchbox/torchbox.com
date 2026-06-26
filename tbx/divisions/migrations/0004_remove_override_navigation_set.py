# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("divisions", "0003_remove_divisionpage_label_divisionpage_logo"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="divisionpage",
            name="override_navigation_set",
        ),
    ]
