# Motif headings

The site makes use of coloured drop-cap letters in major headings, with an optional animation on heading ones.

Because some letters are narrower than others, there was an issue with a large gap after the initial drop-cap, as well as an issue with the letter I where it was too narrow to see the final background flame image. This has been solved with some custom classes for particular letters.

See the `motif-heading.html` component (under `atoms` in the styleguide) and the equivalent `motif-heading.scss` sass file.

There has been an issue with google displaying the heading one without the first letter in search results, probably because of the transparent styling on the first letter. As an attempt to resolve this, for h1s, we now move the motif heading into a paragraph tag, with a visually hidden h1 tag.
