# Generated by Django 4.2.11 on 2024-07-19 09:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0009_add_earth_colour_theme"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="email_text",
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
