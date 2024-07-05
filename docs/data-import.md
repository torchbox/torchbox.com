# Data import

When the current iteration of the site was built (January 2024) we needed to keep the existing blog pages, work pages and team pages.

We kept the model code for these page types, but regenerated the migrations from scratch.

The process of importing the data (via `dumpdata` and `loaddata`) is described in the annexe of the tech spec. You can find a private link, for Torchbox employees only, at https://intranet.torchbox.com/torchbox-com-project-docs.

Streamfield data that did not match with our new definitions had data migrations applied:

- Wide image was mapped to the Image streamfield
- Aligned image was mapped to the new Image streamfield

Note: we subsequently re-added a wide image block, but this is for new images only, not imported ones.

## Work pages and historical work pages

The new work page template has a nested structure with top level headings and child streamfields. The old data could not be mapped across, so we have 2 page types: `HistoricalWorkPage` and `WorkPage`. Editors are prevented in the admin interface from creating new historical work pages, but can edit them.

## Empty streamfield definitions

At the point that the data migrations were created, we still had some references to streamfields we ultimately did not want to keep. Because they are present in migrations we have to keep a reference to them in code, even though they no longer do anything. An example is the `ImageFormatChoiceBlock`.
