# Generated by Django 5.1.4 on 2025-02-20 08:52

from django.db import migrations, models


def label_to_logo(apps, schema_editor):
    DivisionPage = apps.get_model("divisions", "DivisionPage")

    DivisionPage.objects.update(
        logo=models.Case(
            models.When(label="Charity", then=models.Value("logo-charity")),
            models.When(label="Public", then=models.Value("logo-public")),
            models.When(
                label="Wagtail CMS services", then=models.Value("logo-wagtail")
            ),
            default=models.Value("logo-torchbox"),
        )
    )


def logo_to_label(apps, schema_editor):
    DivisionPage = apps.get_model("divisions", "DivisionPage")

    DivisionPage.objects.update(
        logo=models.Case(
            models.When(label="logo-charity", then=models.Value("Charity")),
            models.When(label="logo-public", then=models.Value("Public")),
            models.When(
                label="logo-wagtail", then=models.Value("Wagtail CMS services")
            ),
            default=models.Value(""),
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("divisions", "0002_divisionmixin_and_navigationsetmixin"),
    ]

    operations = [
        migrations.AddField(
            model_name="divisionpage",
            name="logo",
            field=models.CharField(
                choices=[
                    ("logo-torchbox", "Torchbox"),
                    ("logo-charity", "Torchbox Charity"),
                    ("logo-public", "Torchbox Public"),
                    ("logo-wagtail", "Torchbox Wagtail"),
                ],
                default="logo-torchbox",
                max_length=50,
            ),
        ),
        migrations.RunPython(label_to_logo, logo_to_label),
        migrations.RemoveField(
            model_name="divisionpage",
            name="label",
        ),
    ]
