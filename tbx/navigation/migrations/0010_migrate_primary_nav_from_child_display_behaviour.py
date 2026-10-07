# Generated manually
#
# Migrates legacy ``child_display_behaviour`` / ``hide_children`` values on
# the ``primary_navigation`` StreamField into the new ``dropdown_style``,
# ``content_source`` and ``page_children_depth`` fields introduced in 0009.
#
# This migration reads and writes the StreamField column with raw SQL rather
# than going through the ORM. ``apps.get_model(...)`` returns a *historical*
# model whose StreamField isn't fully wired up; reading via ``.values()`` or
# the manager still triggers ``from_db_value``, which returns a ``StreamValue``.
# Any subsequent ``copy.deepcopy(...)`` on that value invokes the pickle
# protocol, and ``StreamValue.__reduce__`` raises:
#
#     "StreamValue can only be pickled if it is associated with a StreamField"
#
# Working with the raw JSON column directly sidesteps StreamValue entirely
# and keeps the migration self-contained.

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


def _load(raw):
    if raw in (None, "", b""):
        return None
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        return json.loads(raw)
    # Some backends (e.g. psycopg with native JSONB) already decode to list/dict.
    if isinstance(raw, list):
        return raw
    return None


def migrate_primary_navigation(apps, schema_editor):
    connection = schema_editor.connection
    table = "navigation_navigationsettings"
    column = "primary_navigation"

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, {column} FROM {table}")  # noqa: S608
        rows = cursor.fetchall()

    for pk, raw in rows:
        stream_data = _load(raw)
        if not stream_data:
            continue

        updated = False
        for block in stream_data:
            if block.get("type") != "link":
                continue

            value = block.setdefault("value", {})
            if value.get("dropdown_style") not in (None, "", "none"):
                # Already migrated / explicitly set — strip any stale legacy
                # keys but leave the new fields alone.
                if value.pop("child_display_behaviour", None) is not None:
                    updated = True
                if value.pop("hide_children", None) is not None:
                    updated = True
                continue

            legacy_behaviour = value.pop("child_display_behaviour", None)
            value.pop("hide_children", None)

            if legacy_behaviour and legacy_behaviour in CHILD_DISPLAY_MIGRATION:
                value.update(CHILD_DISPLAY_MIGRATION[legacy_behaviour])
                updated = True

        if updated:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {table} SET {column} = %s WHERE id = %s",  # noqa: S608
                    [json.dumps(stream_data), pk],
                )


class Migration(migrations.Migration):
    dependencies = [
        ("navigation", "0009_primary_nav_dropdown_fields"),
    ]

    operations = [
        migrations.RunPython(migrate_primary_navigation, migrations.RunPython.noop),
    ]
