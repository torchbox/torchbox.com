# Generated by Django 4.2.9 on 2024-01-30 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0001_initial"),
        ("work", "0018_add_stats_blocks"),
    ]

    operations = [
        migrations.AddField(
            model_name="workpage",
            name="logo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
            ),
        ),
        migrations.AlterField(
            model_name="workpage",
            name="client",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="workpage",
            name="header_image",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
                verbose_name="Image",
            ),
        ),
    ]