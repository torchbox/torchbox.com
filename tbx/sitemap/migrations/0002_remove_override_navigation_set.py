# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sitemap", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sitemappage",
            name="override_navigation_set",
        ),
    ]
