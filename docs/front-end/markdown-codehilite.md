# Markdown block and codehilite

We make use of the [wagtailmarkdown](https://github.com/torchbox/wagtail-markdown) package to provide a markdown block, whose only purpose is to provide a block to add code with syntax highlighting. We could have opted to use [wagtailcodeblock](https://github.com/FlipperPA/wagtailcodeblock) but using `wagtailmarkdown` allowed us to import existing blog posts already using it.

Using headings, text and other formatting in the markdown block will mean pages are not styled correctly. For this reason we have updated the toolbar options in this block to only show the 'code' block. This is done via a custom `admin.js` script which can be used for any admin JavaScript customisations in the future. It is compiled separately to the main site JavaScript in webpack, and called via `core/wagtail_hooks.py`.

`wagtailmarkdown` allows the use of `codehilite` styles for syntax highlighting, from [pygments](https://pygments.org/styles/). We have made use of two themes from pygments - `monokai` for darkmode, and the `default` styles for light mode. Pygments styles aren't available to install via npm, so they are added in a `vendor` folder inside `static_src/sass`, with `stylelint` entirely disabled. There's a simple nesting rule in the CSS to load the `monokai` styles for `.dark-mode` and the `default` styles for `.light-mode`.
