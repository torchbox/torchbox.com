# Generated by Django 2.2.17 on 2021-04-16 13:06

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0023_merge_20210330_1437"),
    ]

    operations = [
        migrations.AlterField(
            model_name="culturepage",
            name="standout_items",
            field=wagtail.fields.StreamField(
                [
                    (
                        "item",
                        wagtail.blocks.StructBlock(
                            [
                                ("title", wagtail.blocks.CharBlock()),
                                ("subtitle", wagtail.blocks.CharBlock()),
                                ("description", wagtail.blocks.TextBlock()),
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "link",
                                    wagtail.blocks.StreamBlock(
                                        [
                                            (
                                                "internal",
                                                wagtail.blocks.PageChooserBlock(),
                                            ),
                                            ("external", wagtail.blocks.URLBlock(),),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
            ),
        ),
    ]
