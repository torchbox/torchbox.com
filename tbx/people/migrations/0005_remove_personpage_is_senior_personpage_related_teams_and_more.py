# Generated by Django 4.2.9 on 2024-02-14 09:36

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0002_sector_team_remove_service_contact_reasons_and_more"),
        ("images", "0001_initial"),
        ("people", "0004_personindexpage_theme_personpage_theme"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="personpage",
            name="is_senior",
        ),
        migrations.AddField(
            model_name="personpage",
            name="related_teams",
            field=modelcluster.fields.ParentalManyToManyField(
                related_name="people", to="taxonomy.team"
            ),
        ),
        migrations.AlterField(
            model_name="personpage",
            name="biography",
            field=wagtail.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name="personpage",
            name="image",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
            ),
        ),
        migrations.AlterField(
            model_name="personpage",
            name="role",
            field=models.CharField(max_length=255),
        ),
    ]
