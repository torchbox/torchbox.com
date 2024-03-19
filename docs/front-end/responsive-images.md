# Responsive images

To create responsive images that will render an appropriate image for the screen size being viewed, we initially used `<picture>` elements with 2 `<source>` elements - one each for mobile and desktop. Each srcset has 2 images, one for non-retina `(1x)`, and one for retina screens (`2x`). See https://docs.wagtail.org/en/v5.2.2/advanced_topics/images/image_file_formats.html#using-the-picture-element.

The above method has quite a bit of processing cost on the back-end, so we are gradually switching to using the `{% srcset_image %}` tag which lets us provide a set of images at different resolutions, and a set of sizes to guide the browser on how to display them. In order to use this, you need to work out what proportion of the screen (or what fixed size) your image takes up at different resolutions. It is a guide rather than necessarily completely accurate. See https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images. A maintenance cost of this is that if the page layout changes, the image's sizes attribute will need updating too, along with the yaml in the pattern library.

We have kept `picture` elements where we have a different aspect ratio at mobile, to give art direction to the browser. Note that we have included width and height attributes on the `srcset` and `img` tags in order to reduce layout shift.

Both `picture` and `srcset_image` images are fully mocked in the pattern library. When updating image tags be sure to update the yaml as well, both for the file you are changing, and potentially in other places such as streamfield templates and the styleguide.
