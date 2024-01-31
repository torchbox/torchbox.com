# Generated by Django 4.2.9 on 2024-01-31 09:47

from django.db import migrations
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtail.snippets.blocks
import wagtailmarkdown.blocks
import wagtailmedia.blocks


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0004_servicepage_featured_blog_heading_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="servicepagefeaturedworkpost",
            name="featured_work_post",
        ),
        migrations.RemoveField(
            model_name="servicepagefeaturedworkpost",
            name="page",
        ),
        migrations.RemoveField(
            model_name="servicepage",
            name="featured_blog_heading",
        ),
        migrations.RemoveField(
            model_name="servicepage",
            name="featured_work_post_heading",
        ),
        migrations.AlterField(
            model_name="servicepage",
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
                                            ("email", wagtail.blocks.EmailBlock()),
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
                    (
                        "partners_block",
                        wagtail.blocks.StructBlock(
                            [
                                ("title", wagtail.blocks.CharBlock(max_length=255)),
                                (
                                    "partner_logos",
                                    wagtail.blocks.ListBlock(
                                        wagtail.images.blocks.ImageChooserBlock(),
                                        label="Logos",
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "showcase",
                        wagtail.blocks.StructBlock(
                            [
                                ("title", wagtail.blocks.CharBlock(max_length=255)),
                                (
                                    "showcase_paragraphs",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                ("heading", wagtail.blocks.CharBlock()),
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
                                            help_text="Add a showcase paragraph, with summary text and an optional page link",
                                            icon="breadcrumb-expand",
                                        ),
                                        help_text="Add at least two showcase paragraphs",
                                        max_num=10,
                                        min_num=2,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "blog_chooser",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "featured_blog_heading",
                                    wagtail.blocks.CharBlock(max_length=255),
                                ),
                                (
                                    "blog_pages",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.PageChooserBlock(
                                            page_type=["blog.BlogPage"]
                                        ),
                                        max_num=3,
                                        min_num=1,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "work_chooser",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "featured_work_heading",
                                    wagtail.blocks.CharBlock(max_length=255),
                                ),
                                (
                                    "work_pages",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.PageChooserBlock(
                                            page_type=[
                                                "work.WorkPage",
                                                "work.HistoricalWorkPage",
                                            ]
                                        ),
                                        max_num=3,
                                        min_num=1,
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                use_json_field=True,
            ),
        ),
        migrations.DeleteModel(
            name="ServicePageFeaturedBlogPost",
        ),
        migrations.DeleteModel(
            name="ServicePageFeaturedWorkPost",
        ),
    ]
