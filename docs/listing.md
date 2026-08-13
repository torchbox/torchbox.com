# Listing filters

Work, News (blog), and Events index pages share a filterable listing UI: three dropdown filters (where applicable), active filter pills, paginated results, and progressive enhancement with htmx.

Configure the underlying taxonomy in **Snippets → Sectors** and **Snippets → Services**. Tag individual blog posts and work pages with **Related sectors** and **Related services** on the page editor.

---

## Listing pages

| Page type             | Model / mixin                                     | Filter template                  | Results template                 |
| --------------------- | ------------------------------------------------- | -------------------------------- | -------------------------------- |
| **Work index**        | `WorkIndexPage` → `build_work_listing_context`    | `listing-filters--taxonomy.html` | `listing_results--work.html`     |
| **Blog / News index** | `BlogIndexPage` → `build_blog_listing_context`    | `listing-filters--taxonomy.html` | `listing_results--taxonomy.html` |
| **Events index**      | `EventIndexPage` → `build_events_listing_context` | `listing-filters--events.html`   | `listing_results--events.html`   |

Each page renders:

1. A **listing header** (`listing-header.html`) with the page title.
2. A **`#listing-panel`** wrapper containing the filter form and results.
3. **`listing.js`** (webpack entry) for dropdown behaviour and htmx initialisation.

---

## Filter dropdowns (Work and News)

Three dropdowns may be shown when each has at least one option on the **unfiltered** listing (or when that dimension has an active selection — see [Dropdown visibility](#dropdown-visibility)):

| Dropdown    | Source                           | Query param | Notes                                                                 |
| ----------- | -------------------------------- | ----------- | --------------------------------------------------------------------- |
| **Sector**  | `Sector` snippets in use         | `sector`    | Repeatable; multiple values OR within param                           |
| **Service** | `Service` snippets (non-culture) | `service`   | Repeatable; excludes culture slugs (see below)                        |
| **Culture** | `Service` snippets (culture set) | `service`   | UI-only split; same param as Service; badge counts culture selections |

Dropdowns with **no options on the unfiltered listing** and **no active selection** in that dimension are hidden (for example, Culture on Work when no culture-tagged work exists). A dropdown is also hidden when the unfiltered listing has exactly **one** option and that option's label matches the dropdown's own label (case-insensitively) — see [Dropdown visibility](#dropdown-visibility). Dropdown visibility is fixed at page load and does not change when facet narrowing removes options after other filters are applied.

**Division** is not shown in the listing UI. Division filtering via `?division=` still works in the backend for legacy URLs. For how divisions relate to site structure and theming, see [Division](custom-features/divisions.md).

### Culture dropdown (UI-only split)

Culture topics (EOT, sustainability, D&I, etc.) are modelled as ordinary **Service** snippets. A curated slug list in code splits services into two dropdowns:

| Constant                | Location                      |
| ----------------------- | ----------------------------- |
| `CULTURE_SERVICE_SLUGS` | `tbx/core/listing/filters.py` |

Default slugs:

- `culture`
- `sustainability`
- `diversity-inclusion`
- `employee-ownership`
- `eot`

Both **Service** and **Culture** checkboxes submit `name="service"`. Filtering, URLs, and active pills behave like any other service filter. This split may be replaced by a dedicated taxonomy later.

**Prerequisites for Culture options to appear:**

1. Create matching **Service** snippets in Wagtail (slug must match an entry in `CULTURE_SERVICE_SLUGS`).
2. Tag at least one published listing item with that service.

If production slugs differ, update `CULTURE_SERVICE_SLUGS` in code.

---

## Filter dropdowns (Events)

| Dropdown       | Source               | Query param | Notes                                                              |
| -------------- | -------------------- | ----------- | ------------------------------------------------------------------ |
| **When**       | Fixed timing options | `timing`    | Two independent checkboxes: `upcoming` and `past`, both repeatable |
| **Event type** | `EventType` snippets | `type`      | Repeatable checkboxes                                              |

Both dropdowns use `filter-dropdown.html` and render checkbox options via `filter-option.html`. Visibility follows the same baseline rules as Work and News (see [Dropdown visibility](#dropdown-visibility)).

**When semantics:** nothing checked is the default view (upcoming events; `has_filters` stays `False` so this doesn't count as an active filter); `upcoming` only shows upcoming events; `past` only shows past events; both checked shows every event, with upcoming events ordered first. Nothing is force-checked in the markup — the default view is a fallback applied when `timings` is empty, not a pre-selected option.

---

## URL query parameters

### Work and News

| Param      | Repeatable | Example                       |
| ---------- | ---------- | ----------------------------- |
| `sector`   | Yes        | `?sector=public-sector`       |
| `service`  | Yes        | `?service=ai&service=culture` |
| `division` | Yes        | Legacy; not exposed in UI     |
| `page`     | No         | `?page=2`                     |

Multiple values for the same param use repeated keys (`?sector=a&sector=b`).

**Legacy:** `?filter={slug}` still resolves to sector, service, or division if the slug matches a valid snippet or division.

### Events

| Param    | Repeatable | Example                        |
| -------- | ---------- | ------------------------------ |
| `timing` | Yes        | `?timing=upcoming&timing=past` |
| `type`   | Yes        | `?type=webinar`                |
| `page`   | No         | `?page=2`                      |

**Legacy:** `?filter=upcoming` or `?filter=past` maps to timing.

### Filter logic

Filtering uses **AND between dimensions** and **OR within a dimension**:

| Scope                                                          | Logic                                                                                 | Example                                                                          |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Different params** (sector, service, division, timing, type) | **AND** — item must match all active dimensions                                       | `?sector=public-sector&service=ai` → posts in that sector **and** tagged with AI |
| **Multiple values for the same param**                         | **OR** — item may match any selected value                                            | `?sector=a&sector=b` → posts in sector A **or** sector B                         |
| **Service + Culture** (both `service`)                         | Values are combined in one param; OR within `service`, AND with `sector` / `division` | `?sector=x&service=ai&service=culture` → sector X **and** (AI **or** culture)    |
| **`timing` (Events)**                                          | OR within the param — checking both shows all events, not the intersection            | `?timing=upcoming&timing=past` → upcoming **or** past, i.e. every event          |

Implementation: `apply_taxonomy_filters()` / `apply_work_page_filters()` apply one ORM filter per active dimension, using `__in` / `Q(... | ...)` within each dimension. Events use the same shape in `filter_events()`.

### Faceted (cross-filter) options

On a full page load, dropdown **options** are narrowed by other active filters so only values that would return results are shown (zero-result options are hidden from the list). During an enhanced filtering session the rendered option lists stay stable: htmx does not replace the controls that the visitor is actively using. This avoids focus loss, visible flicker, and browser instability from replacing a checkbox during its own change event. A reload or direct filtered URL recalculates the facets.

| Facet computed       | Other filters applied                     |
| -------------------- | ----------------------------------------- |
| Sector options       | service, division, culture selections     |
| Service options      | sector, division, culture selections      |
| Culture options      | sector, division, main service selections |
| Event type options   | timing                                    |
| Event timing options | type                                      |

Selected values remain visible even when they would otherwise have no matches (`merge_selected_filter_options` in `filters.py`). Facet helpers: `filter_state_for_facet` in `filters.py`, `_facet_options` in `mixins.py`, `get_available_event_timings` / `get_available_event_types` in `events.py`.

When facet narrowing leaves a dropdown with no options, `filter-options-empty.html` shows an in-dropdown message. When the filtered **results** list is empty, the listing shows a no-results message (see [No results](#no-results)).

### Dropdown visibility

Whether a whole dropdown is shown is computed server-side as `listing_filter_visibility` and passed to `filter-dropdown.html` via `show_dropdown`. A dropdown is visible when:

1. There is an **active selection** in that dimension, or
2. The **unfiltered** listing has options in that dimension, excluding the unhelpful case where its only option has the same label as the dropdown itself (case-insensitively).

Both rules are implemented once, in `dropdown_is_visible` (`tbx/core/listing/filters.py`), and called per dropdown:

| Listing type | Called from                                                   | Location                     |
| ------------ | ------------------------------------------------------------- | ---------------------------- |
| Work / News  | `build_taxonomy_listing_filters` (sector / service / culture) | `tbx/core/listing/mixins.py` |
| Events       | `_event_listing_filter_visibility` (timing / type)            | `tbx/core/listing/events.py` |

Dropdown labels are defined by `DROPDOWN_LABELS` in `filters.py` and passed to the templates as `listing_dropdown_labels`.

When filters are active, visibility uses options from the unfiltered listing (empty `TaxonomyFilterState` / `EventFilterState`), not the facet-narrowed option lists. JavaScript does not hide or show dropdowns after htmx swaps — only badge counts are updated client-side.

### No results

| Listing | Template                         | Message when filters active | Message when unfiltered                                                    |
| ------- | -------------------------------- | --------------------------- | -------------------------------------------------------------------------- |
| Work    | `listing_results--work.html`     | `listing_no_results.html`   | `listing_no_results.html`                                                  |
| News    | `listing_results--taxonomy.html` | `listing_no_results.html`   | `listing_no_results.html`                                                  |
| Events  | `listing_results--events.html`   | `listing_no_results.html`   | Page `no_events_message` or “There are no past events.” for `?timing=past` |

Filtered no-results copy: _“No results match your filters. Try adjusting or clearing your filters.”_

---

## SEO behaviour

Rules are implemented in `build_listing_seo_context` (`tbx/core/listing/filters.py`).

| Active filters | `<title>`                         | `robots`            |
| -------------- | --------------------------------- | ------------------- |
| 0              | Page title                        | (default)           |
| 1              | `{title} filtered by {label}`     | indexable           |
| 2+             | `{title} filtered by {a}, {b}, …` | `noindex, nofollow` |

Canonical URLs are provided by `base_page.html`. Filter parameters are omitted, while pagination is preserved:

| URL                         | Canonical       |
| --------------------------- | --------------- |
| `/news/`                    | `/news/`        |
| `/news/?service=ai`         | `/news/`        |
| `/news/?sector=a&service=b` | `/news/`        |
| `/news/?page=2`             | `/news/?page=2` |

`listing_meta.html` renders the server-side `robots` value when needed. The htmx partial swaps only the document title, since crawlers do not use client-side htmx updates to determine indexing.

---

## htmx behaviour

JavaScript is enabled when `listing.js` is loaded on the listing page. Filter changes use **manual `htmx.ajax` requests** from `listing-filters.js` (the form has no `hx-trigger`; this avoids stale responses and keeps checkbox state in sync with the URL).

### What updates when

| User action               | Swap target              | Also updated (OOB)                |
| ------------------------- | ------------------------ | --------------------------------- |
| Checkbox change           | `[data-listing-results]` | Active filter pills and `<title>` |
| Pagination link           | `[data-listing-results]` | `<title>`                         |
| Remove single filter pill | `[data-listing-results]` | Active filter pills and `<title>` |
| Clear all filters         | `[data-listing-results]` | Active filter pills and `<title>` |

The filter form and dropdown chrome stay in the DOM when only results swap, so an open dropdown can remain open while results and pills update.

Remove/clear links use `hx-params="none"` so checked form values are not merged into the request URL.

After swaps, `syncFilterFormFromUrl()` aligns checkbox state and badge counts with the browser URL. Dropdown visibility is not updated client-side.

**Pagination:** clicking a pagination link scrolls the viewport to the top of `[data-listing-results]` on all htmx-enabled listings (Work, News, Events). Links are marked with `data-listing-pagination` in `pagination.html`.

After an htmx swap, a polite live region announces the updated result count without re-reading the result set.

### Partial response

htmx requests (`HX-Request: true`) return `listing_panel_partial.html`, which includes:

1. OOB document title (`listing_meta_oob.html`)
2. OOB active filters (`listing_active_filters_oob.html`)
3. Panel inner (`listing_panel_inner.html`; htmx selects the results block)

Dropdown option lists are deliberately not OOB-swapped. The form controls remain stable while the results and active-filter pills update.

`listing_base_url` uses the page’s **relative** URL from `page.get_url(request)` so htmx same-origin checks pass in local development.

---

## Non-JavaScript fallback

Without JavaScript:

- Without JavaScript, dropdown option panels render expanded so all checkboxes remain available.
- The filter form submits via **GET** to the listing URL, and the **Apply filters** button (`data-listing-filters-submit`) is visible and does exactly that: the full page reloads with the selected query parameters applied.

With JavaScript, each group becomes a button-controlled disclosure, the Apply button is hidden, and checkbox changes are applied through htmx.

---

## Wagtail admin configuration

### Work and News

| Task                            | Where                                                  |
| ------------------------------- | ------------------------------------------------------ |
| Manage sector labels and slugs  | **Snippets → Sectors**                                 |
| Manage service labels and slugs | **Snippets → Services**                                |
| Tag blog posts                  | Blog page → **Related sectors** / **Related services** |
| Tag work pages                  | Work page → **Related sectors** / **Related services** |

Dropdown options are **derived from the listing’s content**: only sectors and services that appear on at least one item in the index queryset are shown.

**Sort order:** sectors and services respect snippet `sort_order`, then name.

### Events

| Task               | Where                                                    |
| ------------------ | -------------------------------------------------------- |
| Manage event types | **Snippets → Event types** (requires `slug` field)       |
| Event timing       | Fixed in code (`upcoming` / `past`); not edited in admin |

---

## Configuration checklist

Use when setting up or reviewing listing filters:

- [ ] **Sector** and **Service** snippets populated with correct slugs and sort order
- [ ] Culture-related services use slugs listed in `CULTURE_SERVICE_SLUGS`, or update that constant to match CMS
- [ ] Blog and work items tagged with relevant sectors/services
- [ ] Work index, blog index, and events index pages are live
- [ ] Event types have unique slugs
- [ ] Filtered URLs checked: single filter indexable, multiple filters `noindex`
- [ ] Faceted options narrow correctly when combining sector / service filters
- [ ] Dropdowns with no unfiltered options, or with a single option that just repeats the dropdown's own label (e.g. a bare "Culture" option in the Culture dropdown), stay hidden; dropdowns do not hide when facet narrowing empties options after filtering, and an active selection always keeps its dropdown visible
- [ ] No-results message shown when filters return zero items
- [ ] Pagination scrolls to results on Work, News, and Events (with JS enabled)
- [ ] Listing pages load `listing.js` (see page templates under `patterns/pages/work/`, `blog/`, `events/`)
- [ ] Non-JS form submission tested (expanded options and Apply filters)

---

## Front-end behaviour

- **Dropdowns:** button-controlled disclosures using `aria-expanded`; click outside, press Escape, or tab away to close; only one is open at a time. Without JavaScript, the option panels remain expanded.
- **Visibility:** set by `listing_filter_visibility` / `show_dropdown` at page render, via `dropdown_is_visible` in `filters.py`. Shown when there's an active selection, or the unfiltered listing has options beyond a single one that just repeats the dropdown's own label. Doesn't change after filtering or htmx swaps.
- **Counts:** badge on the chevron shows selected count per dropdown (from URL); hidden when zero. Service and Culture badges split counts by `CULTURE_SERVICE_SLUGS` (exposed on the form as `data-listing-culture-service-slugs`).
- **Active filters:** label, pills, and “Clear all filters” below the dropdown row; pills wrap on narrow viewports.
- **Announcements:** a polite `aria-live` region announces the result count after each htmx update.
- **Spacing:** mobile uses tighter gaps between stacked dropdowns and between the filter block and results (`_listing-filters.scss`). Grid placement of the listing header and panel (`grid__listing-header`, `grid__listing-panel`) lives in `components/_grid.scss`, alongside the other grid-column rules.
- **Styles:** `tbx/static_src/sass/components/_listing-filters.scss`, `tbx/static_src/sass/components/_grid.scss`
- **Dropdown JS:** `tbx/static_src/javascript/components/listing-filters.js`
- **htmx entry:** `tbx/static_src/javascript/listing.js` (webpack bundle `listing.js`)

Service and Culture dropdowns use distinct element ids (`id_param` in `filter-dropdown.html`) because both submit `service` params.

---

## Relationship to navigation

The **Work** item in primary navigation can link to filtered views using the legacy `?filter={slug}` param or the explicit params documented above. See [Navigation](navigation.md) → **Work** for nav configuration.

**Sectors** in the header nav link to **division landing pages**. **Sector** on the work/blog listing filters by the **Sector** taxonomy on content — related but not the same mechanism.

---

## Known limitations

| Topic                | Current behaviour                       | Workaround / future                                                |
| -------------------- | --------------------------------------- | ------------------------------------------------------------------ |
| Culture grouping     | Hard-coded slug list in Python          | Add dedicated taxonomy or snippet flag when content model is ready |
| Division filter      | Backend only; not in listing UI         | Use `?division=` if needed; or re-expose dropdown                  |
| Culture vs Service   | Same `service` param; two dropdowns     | Intentional for now                                                |
| Events listing       | Python list filtering, not ORM queryset | Acceptable for current event volume                                |
| Nav `?filter=` links | Still supported via legacy param        | Prefer explicit `?sector=` / `?service=` in new links              |

---

## Related code

| Concern                                               | Location                                                                                         |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Filter state, SEO, dropdown visibility, culture split | `tbx/core/listing/filters.py`                                                                    |
| Selected filters, URLs, SEO context                   | `tbx/core/listing/filters.py` (`build_selected_filter_items`, `build_listing_urls_context`)      |
| Taxonomy filtering (Work / News)                      | `tbx/core/listing/filters.py` (`apply_taxonomy_filters`, `apply_work_page_filters`)              |
| Events filter form                                    | `tbx/core/listing/forms.py` (`EventFilterForm`, lenient fields)                                  |
| Facet option narrowing                                | `tbx/core/listing/mixins.py` (`_facet_options`)                                                  |
| Dropdown visibility (Work / News)                     | `tbx/core/listing/mixins.py` (`build_taxonomy_listing_filters`, calling `dropdown_is_visible`)   |
| Dropdown visibility (Events)                          | `tbx/core/listing/events.py` (`_event_listing_filter_visibility`, calling `dropdown_is_visible`) |
| Work / blog listing context                           | `tbx/core/listing/mixins.py`                                                                     |
| Events listing context                                | `tbx/core/listing/events.py`                                                                     |
| Blog index integration                                | `tbx/blog/models.py` → `BlogIndexPageMixin`                                                      |
| Work index integration                                | `tbx/work/models.py`                                                                             |
| Events index integration                              | `tbx/events/models.py`                                                                           |
| Taxonomy models                                       | `tbx/taxonomy/models.py`                                                                         |
| Filter templates                                      | `tbx/project_styleguide/templates/patterns/molecules/listing-filters/`                           |
| Shared dropdown partial                               | `patterns/molecules/listing-filters/includes/filter-dropdown.html`                               |
| No-results partial                                    | `patterns/pages/listing/includes/listing_no_results.html`                                        |
| `aria-live` announcer                                 | `patterns/pages/listing/listing_panel_inner.html` (`[data-listing-announcer]`)                   |
| OOB partials                                          | `tbx/project_styleguide/templates/patterns/pages/listing/includes/`                              |
| Page / partial templates                              | `tbx/project_styleguide/templates/patterns/pages/listing/`                                       |
| Pagination htmx attrs                                 | `tbx/project_styleguide/templates/patterns/molecules/pagination/pagination.html`                 |
| Grid placement (listing header / panel)               | `tbx/static_src/sass/components/_grid.scss`                                                      |
| Unit / integration tests                              | `tbx/core/listing/tests/`                                                                        |

Run tests:

```bash
DJANGO_SETTINGS_MODULE=tbx.settings.test DATABASE_URL=postgres:///torchbox CFG_SECRET_KEY=test CFG_ALLOWED_HOSTS=localhost poetry run python manage.py test tbx.core.listing.tests
```

---

## Legacy note

Listing pages previously used a **tag cloud** (`title-filters`) with single-select `?filter=` links. That UI has been replaced by the multi-select dropdown filters described here. The `filter` query param remains supported for backwards compatibility with existing links (including primary navigation).

---

???+ note

    Please ensure that the Editors' guide is updated accordingly whenever any changes are made to this feature. A private link, for Torchbox employees only, can be found at https://intranet.torchbox.com/torchbox-com-project-docs.
