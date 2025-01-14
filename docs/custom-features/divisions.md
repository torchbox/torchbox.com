# Divisions

The site's target audience can be grouped into divisions; e.g. the charity division, the public sector division, and the Wagtail division. All content going forward can be associated to one of these divisions.

The idea is that if you're a charity organisation, you can find content that's specific and relevant for you because the relevant content will all be in one place.

This feature allows content to be associated to a specific `DivisionPage`, which allows us to display the same theme, logo and navigation for any content related to a division.

## Options

The available options are dependent on the `DivisionPage`s that have been created.

## Division configuration

The `tbx.core.utils.models.DivisionMixin` provides a mechanism for associating a specific division with a page. It offers the following functionality:

- `division` field: Adds a ForeignKey field to associate a specific division with a page.
- `final_division`: A cached property that determines the appropriate division to associate to a page. It first checks if the page has a `division` specified. If not, it traverses the page's ancestors to find the first page that either has a `division` specified or is a `DivisionPage`, defaulting to `None`.

---

???+ note

    Please ensure that the Editors' guide is updated accordingly whenever any changes are made to this feature. A private link, for Torchbox employees only, can be found at https://intranet.torchbox.com/torchbox-com-project-docs.
