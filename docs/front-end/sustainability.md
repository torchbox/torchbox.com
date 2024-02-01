# Sustainability

In order to make the site more sustainable we must ensure that images are served in a suitable size for the screen they are displayed on, whether they are background images or images loaded with an `<img>` tag.

For the latter, we use a `<picture>` element with 2 `<source>` elements -one each for mobile and desktop. Each srcset has 2 images, one for non-retina `(1x)`, and one for retina screens (`2x`). See https://docs.wagtail.org/en/v5.2.2/advanced_topics/images/image_file_formats.html#using-the-picture-element.

We use lazy loading for all images below the fold.

We use dark mode by default.

All images should be renedered in the template file as webp format using the `format-webp` attribute - see https://docs.wagtail.org/en/v5.2.2/advanced_topics/images/image_file_formats.html.
