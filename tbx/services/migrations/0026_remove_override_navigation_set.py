# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0025_divisionmixin_and_navigationsetmixin"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="serviceareapage",
            name="override_navigation_set",
        ),
        migrations.RemoveField(
            model_name="servicepage",
            name="override_navigation_set",
        ),
    ]
