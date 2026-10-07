# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("torchbox", "0042_delete_mainmenu"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="homepage",
            name="override_navigation_set",
        ),
        migrations.RemoveField(
            model_name="standardpage",
            name="override_navigation_set",
        ),
    ]
