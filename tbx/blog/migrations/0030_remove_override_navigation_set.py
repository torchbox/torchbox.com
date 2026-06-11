# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0029_relatedblogpage"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="blogindexpage",
            name="override_navigation_set",
        ),
        migrations.RemoveField(
            model_name="blogpage",
            name="override_navigation_set",
        ),
    ]
