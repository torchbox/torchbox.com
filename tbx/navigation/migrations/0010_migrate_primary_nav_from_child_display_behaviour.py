# Generated manually

import json

from django.db import migrations

CHILD_DISPLAY_MIGRATION = {
    "hide_children": {
        "dropdown_style": "none",
        "content_source": "manual",
    },
    "show_up_to_level1": {
        "dropdown_style": "mixed_list",
        "content_source": "page_children",
        "page_children_depth": "1",
    },
    "show_up_to_level2": {
        "dropdown_style": "mixed_list",
        "content_source": "page_children",
        "page_children_depth": "2",
    },
}


def migrate_primary_navigation(apps, schema_editor):
    NavigationSettings = apps.get_model("navigation", "NavigationSettings")
    table = NavigationSettings._meta.db_table

    for settings in NavigationSettings.objects.all().iterator():
        stream_data = settings.primary_navigation
        if isinstance(stream_data, str):
            stream_data = json.loads(stream_data)
        if not stream_data:
            continue

        updated = False
        for block in stream_data:
            if block.get("type") != "link":
                continue

            value = block.setdefault("value", {})
            if value.get("dropdown_style") not in (None, "", "none"):
                continue

            legacy_behaviour = value.pop("child_display_behaviour", None)
            value.pop("hide_children", None)

            if legacy_behaviour and legacy_behaviour in CHILD_DISPLAY_MIGRATION:
                value.update(CHILD_DISPLAY_MIGRATION[legacy_behaviour])
                updated = True

        if updated:
            NavigationSettings.objects.filter(pk=settings.pk).update(
                primary_navigation=stream_data
            )


class Migration(migrations.Migration):
    dependencies = [
        ("navigation", "0009_primary_nav_dropdown_fields"),
    ]

    operations = [
        migrations.RunPython(migrate_primary_navigation, migrations.RunPython.noop),
    ]
