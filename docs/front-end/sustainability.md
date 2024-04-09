# Sustainability

In order to make the site more sustainable we must ensure that images are served in a suitable size for the screen they are displayed on, whether they are background images or images loaded with an `<img>` tag. See [Responsive images](responsive-images.md)

We use lazy loading for all images below the fold.

We use dark mode by default.

All images should be renedered in the template file as webp format using the `format-webp` attribute - see https://docs.wagtail.org/en/v5.2.2/advanced_topics/images/image_file_formats.html.

We have a [custom saturation filter](https://github.com/torchbox/torchbox.com/blob/97547c3fc1cefa844d133e3af026c4df0dbca313/tbx/core/wagtail_hooks.py#L76-L90) that allows us to apply a slight desaturation to all images using `saturation-0.6` - this makes the file size of images smaller overall, as well as creating a cohesive look for photographic images.

Youtube videos are not loaded by default. Instead they show a placeholder image and a play button, and only load when the user clicks 'play'.
