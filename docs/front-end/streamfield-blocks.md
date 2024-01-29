# Streamfield blocks and re-usable components

We want our streamfield blocks to be as flexible as possible and re-usable on different page types. Therefore when styling the blocks please apply the following principles:

- Ensure consistent spacing between blocks - make use of the `$spacer` variables provided in `variables.scss`
- Make use of container queries to ensure the blocks display nicely at various widths, regardless of the overall viewport width
- Our flexible grid should ensure that components can be wider or narrower as needed within the page, without the use of bustout code.
- If a component is used for both streamfield and non-streamfield blocks, then use generic variable names (at a single depth, e.g. `title` not `value.title`) which can be passed in from the parent template (e.g. `{% include card.html with title = value.title %}`)
- Some non-streamfield components are also designed for re-use. Examples inluclude the listing components with image and avatar (`listing--image.html` and `listing--avatar.html`) - these are deliberately designed to be included from another template with contextual variables passed in.
- Streamfield blocks are all aligned to the grid system which is done in `grid.scss`. Most streamfields follow a similar pattern of spanning 7 columns on desktop and 4 columns on mobile however this can be changed if needed. The majority of streamfields will start at the 4th column on desktop and 1st column on mobile.
