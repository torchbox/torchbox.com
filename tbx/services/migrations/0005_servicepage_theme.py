# Generated by Django 4.2.9 on 2024-01-30 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0004_servicepage_featured_blog_heading_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicepage",
            name="theme",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "None"),
                    ("theme-coral", "Coral"),
                    ("theme-lagoon", "Lagoon"),
                    ("theme-banana", "Banana"),
                ],
                help_text="The theme will be applied to this page and all of it's descendants. If no theme is selected, it will be derived from this page's ancestors.",
                max_length=25,
            ),
        ),
    ]
