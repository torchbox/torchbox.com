# Generated by Django 4.2.9 on 2024-01-25 12:15

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtail.snippets.blocks
import wagtailmarkdown.blocks
import wagtailmedia.blocks


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("images", "0001_initial"),
        ("torchbox", "0014_alter_standardpage_body"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServicePage",
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
                ("intro", wagtail.fields.RichTextField(blank=True)),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            (
                                "h2",
                                wagtail.blocks.CharBlock(
                                    form_classname="title",
                                    icon="title",
                                    template="patterns/molecules/streamfield/blocks/heading2_block.html",
                                ),
                            ),
                            (
                                "h3",
                                wagtail.blocks.CharBlock(
                                    form_classname="title",
                                    icon="title",
                                    template="patterns/molecules/streamfield/blocks/heading3_block.html",
                                ),
                            ),
                            (
                                "h4",
                                wagtail.blocks.CharBlock(
                                    form_classname="title",
                                    icon="title",
                                    template="patterns/molecules/streamfield/blocks/heading4_block.html",
                                ),
                            ),
                            (
                                "intro",
                                wagtail.blocks.RichTextBlock(
                                    icon="pilcrow",
                                    template="patterns/molecules/streamfield/blocks/intro_block.html",
                                ),
                            ),
                            (
                                "paragraph",
                                wagtail.blocks.RichTextBlock(
                                    icon="pilcrow",
                                    template="patterns/molecules/streamfield/blocks/paragraph_block.html",
                                ),
                            ),
                            (
                                "image",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(),
                                        ),
                                        (
                                            "alt_text",
                                            wagtail.blocks.CharBlock(
                                                help_text="By default the image title (shown above) is used as the alt text. Use this field to provide more specific alt text if required.",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "image_is_decorative",
                                            wagtail.blocks.BooleanBlock(
                                                default=False,
                                                help_text="If checked, this will make the alt text empty.",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "caption",
                                            wagtail.blocks.CharBlock(required=False),
                                        ),
                                        (
                                            "attribution",
                                            wagtail.blocks.CharBlock(required=False),
                                        ),
                                    ],
                                    template="patterns/molecules/streamfield/blocks/image_block.html",
                                ),
                            ),
                            (
                                "call_to_action",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "text",
                                            wagtail.blocks.CharBlock(
                                                max_length=255, required=True
                                            ),
                                        ),
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
                                                    (
                                                        "email",
                                                        wagtail.blocks.EmailBlock(),
                                                    ),
                                                ],
                                                max_num=1,
                                                required=True,
                                            ),
                                        ),
                                    ],
                                    label="Call to Action",
                                    template="patterns/molecules/streamfield/blocks/call_to_action.html",
                                ),
                            ),
                            (
                                "contact_call_to_action",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "call_to_action",
                                            wagtail.blocks.StreamBlock(
                                                [
                                                    (
                                                        "call_to_action",
                                                        wagtail.blocks.StructBlock(
                                                            [
                                                                (
                                                                    "text",
                                                                    wagtail.blocks.CharBlock(
                                                                        max_length=255,
                                                                        required=True,
                                                                    ),
                                                                ),
                                                                (
                                                                    "button_text",
                                                                    wagtail.blocks.CharBlock(
                                                                        max_length=55
                                                                    ),
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
                                                                            (
                                                                                "email",
                                                                                wagtail.blocks.EmailBlock(),
                                                                            ),
                                                                        ],
                                                                        max_num=1,
                                                                        required=True,
                                                                    ),
                                                                ),
                                                            ]
                                                        ),
                                                    )
                                                ],
                                                max_num=1,
                                            ),
                                        ),
                                        (
                                            "person",
                                            wagtail.snippets.blocks.SnippetChooserBlock(
                                                "people.Author"
                                            ),
                                        ),
                                    ],
                                    label="Contact Call to Action",
                                    template="patterns/molecules/streamfield/blocks/contact_call_to_action.html",
                                ),
                            ),
                            (
                                "pullquote",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "quote",
                                            wagtail.blocks.CharBlock(
                                                form_classname="quote title"
                                            ),
                                        ),
                                        ("attribution", wagtail.blocks.CharBlock()),
                                        ("role", wagtail.blocks.CharBlock()),
                                        (
                                            "logo",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                help_text="You may optionally add either a company logo or author image",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "author_image",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                help_text="You may optionally add either a company logo or author image",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "call_to_action",
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
                                    ],
                                    template="patterns/molecules/streamfield/blocks/pullquote_block.html",
                                ),
                            ),
                            (
                                "raw_html",
                                wagtail.blocks.RawHTMLBlock(
                                    icon="code",
                                    label="Raw HTML",
                                    template="patterns/molecules/streamfield/blocks/raw_html_block.html",
                                ),
                            ),
                            (
                                "mailchimp_form",
                                wagtail.blocks.RawHTMLBlock(
                                    icon="code",
                                    label="Mailchimp embedded form",
                                    template="patterns/molecules/streamfield/blocks/mailchimp_form_block.html",
                                ),
                            ),
                            (
                                "markdown",
                                wagtailmarkdown.blocks.MarkdownBlock(
                                    icon="code",
                                    template="patterns/molecules/streamfield/blocks/markdown_block.html",
                                ),
                            ),
                            (
                                "embed",
                                wagtail.embeds.blocks.EmbedBlock(
                                    group="Media",
                                    icon="code",
                                    template="patterns/molecules/streamfield/blocks/embed_block.html",
                                ),
                            ),
                            (
                                "showcase",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(max_length=255),
                                        ),
                                        (
                                            "showcase_paragraphs",
                                            wagtail.blocks.ListBlock(
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "heading",
                                                            wagtail.blocks.CharBlock(),
                                                        ),
                                                        (
                                                            "summary",
                                                            wagtail.blocks.RichTextBlock(),
                                                        ),
                                                        (
                                                            "page",
                                                            wagtail.blocks.PageChooserBlock(
                                                                required=False
                                                            ),
                                                        ),
                                                    ],
                                                    help_text="Add a showcase paragraph, with summary text and an optional link",
                                                    icon="breadcrumb-expand",
                                                ),
                                                max_num=10,
                                                min_num=2,
                                            ),
                                        ),
                                    ],
                                    icon="tasks",
                                    template="patterns/molecules/streamfield/blocks/showcase_block.html",
                                ),
                            ),
                            (
                                "video_block",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "video",
                                            wagtailmedia.blocks.VideoChooserBlock(),
                                        ),
                                        (
                                            "autoplay",
                                            wagtail.blocks.BooleanBlock(
                                                default=False,
                                                help_text="Automatically start and loop the video. Please use sparingly.",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "use_original_width",
                                            wagtail.blocks.BooleanBlock(
                                                default=False,
                                                help_text="Use the original width of the video instead of the default content width. Note that videos wider than the content width will be limited to the content width.",
                                                required=False,
                                            ),
                                        ),
                                    ],
                                    group="Media",
                                ),
                            ),
                        ],
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
    ]
