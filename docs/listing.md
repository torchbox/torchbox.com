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

Three dropdowns are shown when each has at least one option used on that listing:

| Dropdown    | Source                           | Query param | Notes                                                                 |
| ----------- | -------------------------------- | ----------- | --------------------------------------------------------------------- |
| **Sector**  | `Sector` snippets in use         | `sector`    | Repeatable; multiple values OR within param                           |
| **Service** | `Service` snippets (non-culture) | `service`   | Repeatable; excludes culture slugs (see below)                        |
| **Culture** | `Service` snippets (culture set) | `service`   | UI-only split; same param as Service; badge counts culture selections |

Dropdowns with **no options and no active selection** in that dimension are hidden and stay hidden when other filters are applied.

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

| Dropdown       | Source               | Query param | Notes                                 |
| -------------- | -------------------- | ----------- | ------------------------------------- |
| **When**       | Fixed timing options | `timing`    | `upcoming` (default) or `past`; radio |
| **Event type** | `EventType` snippets | `type`      | Repeatable checkboxes                 |

The **When** dropdown is hidden if `listing_filters.timings` is empty (normally always populated).

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

| Param    | Repeatable | Example         |
| -------- | ---------- | --------------- |
| `timing` | No         | `?timing=past`  |
| `type`   | Yes        | `?type=webinar` |
| `page`   | No         | `?page=2`       |

**Legacy:** `?filter=upcoming` or `?filter=past` maps to timing.

### Filter logic

Filtering uses **AND between dimensions** and **OR within a dimension**:

| Scope                                                          | Logic                                                                                 | Example                                                                          |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Different params** (sector, service, division, timing, type) | **AND** — item must match all active dimensions                                       | `?sector=public-sector&service=ai` → posts in that sector **and** tagged with AI |
| **Multiple values for the same param**                         | **OR** — item may match any selected value                                            | `?sector=a&sector=b` → posts in sector A **or** sector B                         |
| **Service + Culture** (both `service`)                         | Values are combined in one param; OR within `service`, AND with `sector` / `division` | `?sector=x&service=ai&service=culture` → sector X **and** (AI **or** culture)    |

Implementation: `apply_taxonomy_filters` / `apply_work_page_filters` in `tbx/core/listing/filters.py` chain `.filter(...__slug__in=...)` per dimension (`__in` is OR). Events use the same pattern in `filter_events` (`events.py`): timing narrows the list, then any selected `type` matches via OR.

### Faceted (cross-filter) options

Dropdown options are **narrowed by other active filters** so only values that would return results are shown (zero-result options are hidden).

| Facet computed       | Other filters applied                     |
| -------------------- | ----------------------------------------- |
| Sector options       | service, division, culture selections     |
| Service options      | sector, division, culture selections      |
| Culture options      | sector, division, main service selections |
| Event type options   | timing                                    |
| Event timing options | type                                      |

Selected values remain visible even when they would otherwise have no matches (`merge_selected_filter_options` in `filters.py`). Facet helpers: `filter_state_for_facet`, `_build_facet_taxonomy_listing_filters` in `mixins.py`, `get_available_event_timings` / `get_available_event_types` in `events.py`.

---

## SEO behaviour

Rules are implemented in `build_listing_seo_context` (`tbx/core/listing/filters.py`).

| Active filters | `<title>`                         | `robots`            | Canonical                                       |
| -------------- | --------------------------------- | ------------------- | ----------------------------------------------- |
| 0              | Page title                        | (default)           | Base URL if `?page=` present; else page default |
| 1              | `{title} filtered by {label}`     | indexable           | Current filtered URL                            |
| 2+             | `{title} filtered by {a}, {b}, …` | `noindex, nofollow` | Base listing URL                                |

Meta tags are always rendered with stable ids (`#document-robots`, `#document-canonical`) so htmx out-of-band swaps can update them without console errors.

Templates: `listing_meta.html` (full page), `listing_meta_oob.html` (htmx partial).

---

## htmx behaviour

JavaScript is enabled when `listing.js` is loaded on the listing page. Filter changes use **manual `htmx.ajax` requests** from `listing-filters.js` (the form has no `hx-trigger`; this avoids stale responses and keeps checkbox state in sync with the URL).

### What updates when

| User action               | Swap target               | Also updated (OOB)                                        |
| ------------------------- | ------------------------- | --------------------------------------------------------- |
| Checkbox / radio change   | `.listing-panel__results` | Active filter pills, dropdown option lists, document meta |
| Pagination link           | `.listing-panel__results` | Document meta                                             |
| Remove single filter pill | `.listing-panel__results` | Active filter pills, dropdown option lists, document meta |
| Clear all filters         | `.listing-panel__results` | Active filter pills, dropdown option lists, document meta |

The filter form and dropdown chrome stay in the DOM when only results swap, so an open dropdown can remain open while results and pills update.

Remove/clear links use `hx-params="none"` so checked form values are not merged into the request URL.

After swaps, `syncFilterFormFromUrl()` aligns checkbox/radio state and badge counts with the browser URL. Badge counts are derived from URL parameters (or pending form values while a change is debounced), not from unchecked DOM state.

**Pagination:** clicking a pagination link scrolls the viewport to the top of `.listing-panel__results` on all htmx-enabled listings (Work, News, Events). Links are marked with `data-listing-pagination` in `pagination.html`.

### Partial response

htmx requests (`HX-Request: true`) return `listing_panel_partial.html`, which includes:

1. OOB meta (`listing_meta_oob.html`)
2. OOB active filters (`listing_active_filters_oob.html`)
3. OOB dropdown option lists (`listing_taxonomy_filter_options_oob.html` or `listing_events_filter_options_oob.html`)
4. Panel inner (`listing_panel_inner.html` — filters + results; htmx selects only the results block when configured)

`listing_base_url` uses the page’s **relative** URL from `page.get_url(request)` so htmx same-origin checks pass in local development.

---

## Non-JavaScript fallback

Without JavaScript:

- The filter form submits via **GET** to the listing URL.
- An **Apply filters** button is visible (`data-listing-filters-submit`).
- The full page reloads with query parameters applied.

With JavaScript, the Apply button is hidden and changes apply automatically (debounced 200ms on input change).

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
- [ ] Empty dropdowns (e.g. Culture on Work) stay hidden after applying other filters
- [ ] Pagination scrolls to results on Work, News, and Events (with JS enabled)
- [ ] Listing pages load `listing.js` (see page templates under `patterns/pages/work/`, `blog/`, `events/`)
- [ ] Non-JS form submission tested (Apply filters)

---

## Front-end behaviour

- **Dropdowns:** click toggle to open; click outside or press Escape to close; only one open at a time. Panels are hidden with CSS when closed (not the `hidden` attribute), so closed checkboxes are still submitted correctly.
- **Visibility:** a dropdown is shown only when it has at least one option **or** at least one active selection in that dimension. Empty dropdowns are not revealed when other filters are applied.
- **Counts:** badge on the chevron shows selected count per dropdown (from URL); hidden when zero. Service and Culture badges split counts by `CULTURE_SERVICE_SLUGS` (exposed on the form as `data-listing-culture-service-slugs`).
- **Active filters:** label, pills, and “Clear all filters” below the dropdown row; pills wrap on narrow viewports.
- **Spacing:** mobile uses tighter gaps between stacked dropdowns and between the filter block and results (`_listing-filters.scss`).
- **Styles:** `tbx/static_src/sass/components/_listing-filters.scss`
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

| Concern                          | Location                                                                         |
| -------------------------------- | -------------------------------------------------------------------------------- |
| Filter state, SEO, culture split | `tbx/core/listing/filters.py`                                                    |
| Facet option narrowing           | `tbx/core/listing/mixins.py` (`_build_facet_taxonomy_listing_filters`)           |
| Work / blog listing context      | `tbx/core/listing/mixins.py`                                                     |
| Events listing context           | `tbx/core/listing/events.py`                                                     |
| Blog index integration           | `tbx/blog/models.py` → `BlogIndexPageMixin`                                      |
| Work index integration           | `tbx/work/models.py`                                                             |
| Events index integration         | `tbx/events/models.py`                                                           |
| Taxonomy models                  | `tbx/taxonomy/models.py`                                                         |
| Filter templates                 | `tbx/project_styleguide/templates/patterns/molecules/listing-filters/`           |
| OOB partials                     | `tbx/project_styleguide/templates/patterns/pages/listing/includes/`              |
| Page / partial templates         | `tbx/project_styleguide/templates/patterns/pages/listing/`                       |
| Pagination htmx attrs            | `tbx/project_styleguide/templates/patterns/molecules/pagination/pagination.html` |
| Unit / integration tests         | `tbx/core/listing/tests/`                                                        |

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
