# Generated by Django 4.2.8 on 2024-01-02 10:49

from django.db import migrations, models
import django.db.models.deletion

import modelcluster.fields
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("people", "0001_initial"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("images", "0001_initial"),
        ("taxonomy", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventIndexPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("social_text", models.CharField(blank=True, max_length=255)),
                (
                    "call_to_action",
                    wagtail.fields.StreamField(
                        [
                            (
                                "key_points_summary",
                                wagtail.blocks.ListBlock(
                                    wagtail.blocks.StructBlock(
                                        [
                                            ("title", wagtail.blocks.CharBlock()),
                                            ("intro", wagtail.blocks.CharBlock()),
                                            ("link", wagtail.blocks.PageChooserBlock()),
                                        ]
                                    ),
                                    help_text="Please add a minumum of 3 and a maximum of 6 key points.",
                                    icon="list-ul",
                                    max_num=6,
                                    min_num=3,
                                    template="patterns/molecules/streamfield/blocks/key_points_summary.html",
                                ),
                            ),
                            (
                                "testimonials",
                                wagtail.blocks.ListBlock(
                                    wagtail.blocks.StructBlock(
                                        [
                                            (
                                                "quote",
                                                wagtail.blocks.CharBlock(
                                                    form_classname="quote title"
                                                ),
                                            ),
                                            ("name", wagtail.blocks.CharBlock()),
                                            ("role", wagtail.blocks.CharBlock()),
                                            (
                                                "link",
                                                wagtail.blocks.StreamBlock(
                                                    [
                                                        (
                                                            "internal_link",
                                                            wagtail.blocks.StructBlock(
                                                                [
                                                                    (
                                                                        "page",
                                                                        wagtail.blocks.PageChooserBlock(),
                                                                    ),
                                                                    (
                                                                        "link_text",
                                                                        wagtail.blocks.CharBlock(
                                                                            required=False
                                                                        ),
                                                                    ),
                                                                ]
                                                            ),
                                                        ),
                                                        (
                                                            "external_link",
                                                            wagtail.blocks.StructBlock(
                                                                [
                                                                    (
                                                                        "link_url",
                                                                        wagtail.blocks.URLBlock(
                                                                            label="URL"
                                                                        ),
                                                                    ),
                                                                    (
                                                                        "link_text",
                                                                        wagtail.blocks.CharBlock(),
                                                                    ),
                                                                ]
                                                            ),
                                                        ),
                                                    ],
                                                    required=False,
                                                ),
                                            ),
                                        ]
                                    ),
                                    icon="openquote",
                                    template="patterns/molecules/streamfield/blocks/testimonial_block.html",
                                ),
                            ),
                            (
                                "clients",
                                wagtail.blocks.ListBlock(
                                    wagtail.blocks.StructBlock(
                                        [
                                            (
                                                "image",
                                                wagtail.images.blocks.ImageChooserBlock(),
                                            ),
                                            (
                                                "link",
                                                wagtail.blocks.StreamBlock(
                                                    [
                                                        (
                                                            "internal_link",
                                                            wagtail.blocks.StructBlock(
                                                                [
                                                                    (
                                                                        "page",
                                                                        wagtail.blocks.PageChooserBlock(),
                                                                    ),
                                                                    (
                                                                        "link_text",
                                                                        wagtail.blocks.CharBlock(
                                                                            required=False
                                                                        ),
                                                                    ),
                                                                ]
                                                            ),
                                                        ),
                                                        (
                                                            "external_link",
                                                            wagtail.blocks.StructBlock(
                                                                [
                                                                    (
                                                                        "link_url",
                                                                        wagtail.blocks.URLBlock(
                                                                            label="URL"
                                                                        ),
                                                                    ),
                                                                    (
                                                                        "link_text",
                                                                        wagtail.blocks.CharBlock(),
                                                                    ),
                                                                ]
                                                            ),
                                                        ),
                                                    ],
                                                    required=False,
                                                ),
                                            ),
                                        ]
                                    ),
                                    icon="site",
                                    label="Clients logo",
                                    template="patterns/molecules/streamfield/blocks/client-logo-block.html",
                                ),
                            ),
                            (
                                "embed_plus_cta",
                                wagtail.blocks.StructBlock(
                                    [
                                        ("title", wagtail.blocks.CharBlock()),
                                        ("intro", wagtail.blocks.CharBlock()),
                                        (
                                            "link",
                                            wagtail.blocks.PageChooserBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "external_link",
                                            wagtail.blocks.URLBlock(
                                                label="External Link", required=False
                                            ),
                                        ),
                                        ("button_text", wagtail.blocks.CharBlock()),
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "embed",
                                            wagtail.embeds.blocks.EmbedBlock(
                                                label="Youtube Embed", required=False
                                            ),
                                        ),
                                    ],
                                    icon="code",
                                    label="Embed + CTA",
                                    template="patterns/molecules/streamfield/blocks/embed_plus_cta_block.html",
                                ),
                            ),
                            (
                                "cta",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "text",
                                            wagtail.blocks.CharBlock(
                                                help_text="Words in  &lt;span&gt; tag will display in a contrasting colour."
                                            ),
                                        ),
                                        (
                                            "link",
                                            wagtail.blocks.StreamBlock(
                                                [
                                                    (
                                                        "internal_link",
                                                        wagtail.blocks.StructBlock(
                                                            [
                                                                (
                                                                    "page",
                                                                    wagtail.blocks.PageChooserBlock(),
                                                                ),
                                                                (
                                                                    "link_text",
                                                                    wagtail.blocks.CharBlock(
                                                                        required=False
                                                                    ),
                                                                ),
                                                            ]
                                                        ),
                                                    ),
                                                    (
                                                        "external_link",
                                                        wagtail.blocks.StructBlock(
                                                            [
                                                                (
                                                                    "link_url",
                                                                    wagtail.blocks.URLBlock(
                                                                        label="URL"
                                                                    ),
                                                                ),
                                                                (
                                                                    "link_text",
                                                                    wagtail.blocks.CharBlock(),
                                                                ),
                                                            ]
                                                        ),
                                                    ),
                                                ]
                                            ),
                                        ),
                                    ],
                                    icon="plus-inverse",
                                    template="patterns/molecules/streamfield/blocks/cta.html",
                                ),
                            ),
                        ],
                        blank=True,
                        use_json_field=True,
                    ),
                ),
                (
                    "social_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                ("title", models.CharField(max_length=255)),
                ("intro", models.TextField(verbose_name="Description")),
                ("link_external", models.URLField(verbose_name="External link")),
                ("date", models.DateField(verbose_name="Event date")),
                ("event_type", models.CharField(max_length=30)),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="authors",
                        to="people.author",
                        verbose_name="Host",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="events.eventindexpage",
                    ),
                ),
                (
                    "related_services",
                    modelcluster.fields.ParentalManyToManyField(
                        related_name="events", to="taxonomy.service"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
