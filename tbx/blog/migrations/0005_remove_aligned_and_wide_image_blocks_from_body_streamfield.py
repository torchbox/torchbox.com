# Generated by Django 4.2.9 on 2024-01-15 11:53

from django.db import migrations
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtailmarkdown.blocks
import wagtailmedia.blocks


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0004_data_migration_aligned_and_wide_images"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogpage",
            name="body",
            field=wagtail.fields.StreamField(
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
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                ("alt_text", wagtail.blocks.CharBlock(required=False)),
                                (
                                    "image_is_decorative",
                                    wagtail.blocks.BooleanBlock(
                                        default=False,
                                        help_text="If checked, this will make the alt text empty.",
                                        required=False,
                                    ),
                                ),
                                ("caption", wagtail.blocks.CharBlock(required=False)),
                                (
                                    "attribution",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                            ],
                            template="patterns/molecules/streamfield/blocks/image_block.html",
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
                        "video_block",
                        wagtail.blocks.StructBlock(
                            [
                                ("video", wagtailmedia.blocks.VideoChooserBlock()),
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
    ]
