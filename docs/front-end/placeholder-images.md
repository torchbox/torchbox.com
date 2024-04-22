# Using Unsplash Source or Picsum for placeholder images

## Using picsum

Use picsum for any new yaml templates that override image tags. At some point in the near future we will migrate all yaml files to use picsum.

The benefits of picsum:

- Allows webp
- Does not rely on readig cross-site cookies
- Faster than Unsplash

You can choose a specific image by browsing their library at https://picsum.photos/images
Or use a random image: https://picsum.photos/540/190.webp

Generate a selection of images in different formats, all using the same seed image:

https://picsum.photos/seed/picsum/200/300.webp
https://picsum.photos/seed/picsum/1000/1000.webp
https://picsum.photos/seed/picsum/2900/300.webp

## Using Unspash

Note that we are now moving away from using Unsplash, as the method of querying images described below is no longer documented, and because it requires reading cross-site cookies that will soon be blocked by chrome.

Images can be queried using the url `https://source.unsplash.com` followed by the endpoints `/random`, `/featured`, `/user/{USERNAME}`, `/collection/{COLLECTION ID}` and `/{PHOTO ID}`.

Image sizes can be specified by appending to the end of the url, `https://source.unsplash.com/random/1080x720`.

Search terms can be also be applied to all endpoints with the exception of `{PHOTO ID}` by providing a comma separated list after a question mark, `https://source.unsplash.com/random/?mountain,forest`.

For more information about each endpoint see https://source.unsplash.com/.

Source is built for "small, low-traffic applications". If you want to use Unsplash in production, outside of the pattern-library, use the official Unsplash API. By creating a developer account you will also have access to more features such as lists, pagination, statistics and authentication. For more information look at the Unsplash API [documentation](https://unsplash.com/documentation) and consider using [wagtail-unsplash](https://github.com/jafacakes2011/wagtail-unsplash).
