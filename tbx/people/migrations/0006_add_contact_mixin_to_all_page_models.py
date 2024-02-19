# Generated by Django 4.2.9 on 2024-02-16 10:11

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        (
            "people",
            "0005_remove_personpage_is_senior_personpage_related_teams_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="contact",
            name="email_address",
        ),
        migrations.RemoveField(
            model_name="contact",
            name="phone_number",
        ),
        migrations.AddField(
            model_name="contact",
            name="cta",
            field=wagtail.fields.StreamField(
                [
                    (
                        "call_to_action",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "button_text",
                                    wagtail.blocks.CharBlock(max_length=55),
                                ),
                                (
                                    "button_link",
                                    wagtail.blocks.StreamBlock(
                                        [
                                            (
                                                "internal_link",
                                                wagtail.blocks.PageChooserBlock(),
                                            ),
                                            (
                                                "external_link",
                                                wagtail.blocks.URLBlock(),
                                            ),
                                            ("email", wagtail.blocks.EmailBlock()),
                                        ],
                                        max_num=1,
                                        required=True,
                                    ),
                                ),
                            ],
                            label="CTA",
                        ),
                    )
                ],
                blank=True,
                use_json_field=True,
            ),
        ),
        migrations.AddField(
            model_name="contact",
            name="text",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="contact",
            name="title",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="personindexpage",
            name="contact",
            field=models.ForeignKey(
                blank=True,
                help_text="The contact will be applied to this page's footer and all of its descendants.\nIf no contact is selected, it will be derived from this page's ancestors, eventually falling back to the default contact.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="people.contact",
            ),
        ),
        migrations.AddField(
            model_name="personpage",
            name="contact",
            field=models.ForeignKey(
                blank=True,
                help_text="The contact will be applied to this page's footer and all of its descendants.\nIf no contact is selected, it will be derived from this page's ancestors, eventually falling back to the default contact.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="people.contact",
            ),
        ),
        migrations.AlterField(
            model_name="contact",
            name="default_contact",
            field=models.BooleanField(
                blank=True,
                default=False,
                help_text="Make this the default contact for the site. Setting this will override any existing default.",
                null=True,
            ),
        ),
    ]