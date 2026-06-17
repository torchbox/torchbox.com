# Generated manually

import copy
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


def get_raw_stream_data(value):
    if not value:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return json.loads(value)
    raw_data = getattr(value, "raw_data", None) or getattr(value, "_raw_data", None)
    if raw_data is not None:
        return raw_data
    raise TypeError(f"Cannot read stream data from {type(value)!r}")


def migrate_primary_navigation(apps, schema_editor):
    NavigationSettings = apps.get_model("navigation", "NavigationSettings")
    table = NavigationSettings._meta.db_table
    quoted_table = schema_editor.quote_name(table)

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"SELECT id, primary_navigation FROM {quoted_table}")  # noqa: S608
        rows = list(cursor.fetchall())

    for pk, stream_data in rows:
        stream_data = get_raw_stream_data(stream_data)
        if not stream_data:
            continue

        stream_data = copy.deepcopy(stream_data)
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
            NavigationSettings.objects.filter(pk=pk).update(
                primary_navigation=stream_data
            )


class Migration(migrations.Migration):
    dependencies = [
        ("navigation", "0009_primary_nav_dropdown_fields"),
    ]

    operations = [
        migrations.RunPython(migrate_primary_navigation, migrations.RunPython.noop),
    ]
