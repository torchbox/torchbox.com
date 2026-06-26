# Generated manually for primary navigation dropdown support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("navigation", "0008_navigationsettings_footer_newsletter_cta"),
    ]

    operations = [
        migrations.AddField(
            model_name="navigationsettings",
            name="header_cta_page",
            field=models.ForeignKey(
                blank=True,
                help_text="Page linked from the header “Get in touch” button.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
            ),
        ),
        migrations.AddField(
            model_name="navigationsettings",
            name="header_cta_text",
            field=models.CharField(
                blank=True,
                default="Get in touch",
                help_text="Text for the header “Get in touch” button.",
                max_length=255,
            ),
        ),
    ]
