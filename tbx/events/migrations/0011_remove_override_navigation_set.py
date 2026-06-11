# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0010_divisionmixin_and_navigationsetmixin"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="eventindexpage",
            name="override_navigation_set",
        ),
    ]
