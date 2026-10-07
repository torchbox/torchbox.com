# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("impact_reports", "0007_add_alt_text_to_impact_report_hero_image"),
        ("navigation", "0010_migrate_primary_nav_from_child_display_behaviour"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="impactreportpage",
            name="override_navigation_set",
        ),
    ]
