# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0012_divisionmixin_and_navigationsetmixin"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="personindexpage",
            name="override_navigation_set",
        ),
        migrations.RemoveField(
            model_name="personpage",
            name="override_navigation_set",
        ),
    ]
