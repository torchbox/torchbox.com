# Streamfield blocks

We want our streamfield blocks to be as flexible as possible and re-usable on different page types. Therefore when styling the blocks please apply the following principles:

- Ensure consistent spacing between blocks
- Make use of container queries to ensure the blocks display nicely at various widths, regardless of the overall viewport width
- Our flexible grid should ensure that components can be wider or narrower as needed within the page, without the use of bustout code.
- If a component is used for both streamfield and non-streamfield blocks, then use generic variable names (at a single depth, e.g. `title` not `value.title`) which can be passed in from the parent template (e.g. `{% include card.html with title = value.title %}`)
