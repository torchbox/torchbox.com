from django.db import migrations, models
from django.utils.text import slugify


def populate_event_type_slugs(apps, schema_editor):
    EventType = apps.get_model("torchbox", "EventType")
    used_slugs = set()
    for event_type in EventType.objects.all().order_by("pk"):
        base_slug = slugify(event_type.name) or "event-type"
        slug = base_slug
        suffix = 2
        while slug in used_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        used_slugs.add(slug)
        event_type.slug = slug
        event_type.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("torchbox", "0043_remove_override_navigation_set"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventtype",
            name="slug",
            field=models.SlugField(max_length=255, null=True, db_index=False),
        ),
        migrations.RunPython(
            populate_event_type_slugs,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="eventtype",
            name="slug",
            field=models.SlugField(
                max_length=255,
                unique=True,
                help_text="Used as the value in event-filter URLs. "
                "Changing it will break existing filter links.",
            ),
        ),
    ]
