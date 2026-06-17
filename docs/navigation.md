# Navigation

Site information architecture is exposed through **primary navigation** dropdowns in the header. There is no separate secondary navigation layer.

Configure navigation in **Settings → Navigation settings**.

## Primary navigation fields

Each item in the primary navigation stream supports:

| Field                            | Purpose                                                                                       |
| -------------------------------- | --------------------------------------------------------------------------------------------- |
| **Page / External link**         | Top-level destination. One is required.                                                       |
| **Navigation text**              | Label shown in the header. Defaults to the page title.                                        |
| **Dropdown style**               | Layout for the dropdown panel (desktop). Choose “No dropdown” for a plain link.               |
| **Content source**               | Where dropdown links come from. Manual link fields are only used when this is “Manual links”. |
| **Secondary / Promoted heading** | Optional column headings in the dropdown.                                                     |
| **Secondary links**              | Manual main-column links (with description, tags, accent colour).                             |
| **Promoted links**               | Manual featured links (with description).                                                     |
| **Page children depth**          | Only used with “Auto-generate from page children”. Respects “Show in menus” on child pages.   |

If a dropdown style is set but no links can be resolved, the item renders as a plain link (no chevron).

---

## Dropdown styles

There are three dropdown layouts (plus “No dropdown” for plain header links). On mobile, all dropdown styles use the same drill-down panel (flat list with optional promoted section).

| Style                           | Best for                        | Desktop layout                                                                 |
| ------------------------------- | ------------------------------- | ------------------------------------------------------------------------------ |
| **Teaser grid / card list**     | Division pages, visual cards    | Main column as a card grid; optional promoted column as a featured list         |
| **Mixed list + featured links** | Services, Thinking, About     | Left: links with descriptions and arrows; right: bordered featured cards       |
| **Taxonomy index**              | Work filtered by sector/service | Left: sector list (title + optional tags); right: compact service link grid    |
| **No dropdown**                 | Simple top-level links          | Plain header link (no chevron)                                                 |

### Style → template mapping

| Dropdown style              | Desktop template                         |
| --------------------------- | ---------------------------------------- |
| Teaser grid / card list     | `primary-nav-dropdown-teaser-grid.html`  |
| Mixed list + featured links | `primary-nav-dropdown-mixed-list.html`   |
| Taxonomy index              | `primary-nav-dropdown-taxonomy-index.html` |

---

## Content sources

| Source                                 | Populates                                                                                                                                        |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Manual links**                       | Secondary and promoted link streams edited in Navigation settings                                                                                |
| **Auto-generate from division pages**  | All live `DivisionPage` records (nav text, search description, theme accent)                                                                     |
| **Auto-generate sectors and services** | `Sector` snippets in the main column; `Service` snippets in the promoted column (links to work index with `?filter=`)                            |
| **Auto-generate from page children**   | Children (and optionally grandchildren) of the selected top-level page with **Show in menus** enabled                                            |

### What each auto source reads

| Source              | Link text              | Description                          | Tags          | Accent colour     | URL                    |
| ------------------- | ---------------------- | ------------------------------------ | ------------- | ----------------- | ---------------------- |
| Division pages      | Page **Navigation text** | Page **Search description**        | —             | Page **Theme**    | Division page URL      |
| Sectors             | Snippet **Name**       | Snippet **Description**            | —             | —                 | `/work/?filter={slug}` |
| Services            | Snippet **Name**       | —                                    | —             | —                 | `/work/?filter={slug}` |
| Page children       | Child **Navigation text** | Child **Search description**    | —             | —                 | Child page URL         |

Manual **secondary links** support description, tags (middle-dot separated), and accent colour. Manual **promoted links** support description only.

---

## IA prototype mapping

The new IA prototype defines five primary nav items. Each maps to one dropdown style and one content source:

| Prototype item | Dropdown style              | Content source                     | Prototype layout                                                                 |
| -------------- | --------------------------- | ---------------------------------- | -------------------------------------------------------------------------------- |
| **Sectors**    | Teaser grid / card list     | Auto-generate from division pages  | 2×2 card grid: Charities, Health, Public sector, GLAM with accent bars           |
| **Services**   | Mixed list + featured links | Manual links                       | Left: core services list; right: quick-start engagement cards                    |
| **Work**       | Taxonomy index              | Auto-generate sectors and services | Left: by sector (with sub-labels); right: by service (compact grid)             |
| **Thinking**   | Mixed list + featured links | Page children + manual promoted    | Left: News, Insights, Events; right: latest insight cards                        |
| **About**      | Mixed list + featured links | Page children + manual promoted    | Left: Careers, Culture, Team; right: employee ownership / values cards           |

**Sectors vs Work:** both show similar sector names but serve different purposes. **Sectors** links to division landing pages. **Work** links to filtered views on the work index (`/work/?filter=…`).

---

## Wagtail admin configuration

Configure in **Settings → Navigation settings → Primary navigation**. Add one **link** block per top-level item, in menu order.

### 1. Sectors

| Field               | Value                                      |
| ------------------- | ------------------------------------------ |
| Page                | Sectors index page (or relevant landing page) |
| Navigation text     | `Sectors`                                  |
| Dropdown style      | **Teaser grid / card list**                |
| Content source      | **Auto-generate from division pages**    |
| Secondary heading   | `Sectors we support`                       |
| Promoted heading    | Leave blank unless using a promoted column |
| Secondary links     | Leave empty (auto-generated)               |
| Promoted links      | Leave empty unless adding a promoted column manually |

**Prerequisites:**

- Live **DivisionPage** records exist (Charities, Health, Public sector, GLAM, etc.).
- Each division page has a **Search description** (card body copy) and **Theme** set on the Promote tab (drives accent bar colour).
- Override labels with **Navigation text** on each division page if needed.

**Tags on cards (prototype):** auto-generated division links do not include tags. To show sub-labels like “Health charities · International development”, either switch to **Manual links** with the **tags** field, or extend the division page model / resolver (not implemented today).

---

### 2. Services

| Field               | Value                                      |
| ------------------- | ------------------------------------------ |
| Page                | Services index page                        |
| Navigation text     | `Services`                                 |
| Dropdown style      | **Mixed list + featured links**            |
| Content source      | **Manual links**                           |
| Secondary heading   | `Core services`                            |
| Promoted heading    | `Quick-start engagements`                  |

**Secondary links** (main column — link text, page/URL, description):

| Link text              | Typical destination        |
| ---------------------- | -------------------------- |
| AI & Automation        | Service landing page       |
| Data & analytics       | Service landing page       |
| Digital marketing      | Service landing page       |
| Digital transformation | Service landing page       |
| Research & design      | Service landing page       |
| SEO & AEO              | Service landing page       |
| Websites & platforms   | Service landing page       |

**Promoted links** (featured column — link text, page/URL, description):

| Link text              | Description (example)                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------- |
| AI Co-Fund             | Torchbox co-invests alongside you to explore AI opportunities and build a roadmap.   |
| EEAT Review            | Assess your search authority and content credibility for AI search.                  |
| Possibility Mapping    | Explore what's achievable — ideal for early-stage thinking.                          |
| Roadmapping Workshop   | Define your digital direction in a focused half-day.                                 |
| Website Audit          | Performance, accessibility, SEO and content reviewed in full.                        |

All content is edited in Navigation settings; no automatic sync with the page tree.

---

### 3. Work

| Field               | Value                                      |
| ------------------- | ------------------------------------------ |
| Page                | **Work index page** (`WorkIndexPage`)      |
| Navigation text     | `Work`                                     |
| Dropdown style      | **Taxonomy index**                         |
| Content source      | **Auto-generate sectors and services**     |
| Secondary heading   | `By sector` (default if left blank)        |
| Promoted heading    | `By service` (default if left blank)       |
| Secondary links     | Leave empty (auto-generated)               |
| Promoted links      | Leave empty (auto-generated)               |

**Prerequisites:**

- A live **Work index page** exists.
- **Snippets → Sectors** populated (name, slug, description, sort order).
- **Snippets → Services** populated (name, slug, sort order).

Links resolve to `{work_index_url}?filter={slug}`.

**Sector sub-labels (prototype):** the taxonomy index template supports **tags**, but auto-generated sector links do not populate them. Use manual secondary links for tagged sector rows, or extend `_auto_taxonomy_sectors` in `tbx/navigation/utils.py`.

---

### 4. Thinking

| Field               | Value                                      |
| ------------------- | ------------------------------------------ |
| Page                | Thinking / blog index page                 |
| Navigation text     | `Thinking`                                 |
| Dropdown style      | **Mixed list + featured links**            |
| Content source      | **Auto-generate from page children**       |
| Page children depth | **Children only**                          |
| Secondary heading   | `Thinking`                                 |
| Promoted heading    | `Latest insights`                          |

**Prerequisites (left column — auto):**

- Child pages under the Thinking index with **Show in menus** enabled, e.g. News, Insights, Events index pages.
- Each child has a **Search description** for the dropdown blurb.

**Promoted links (right column — manual):**

Curate 2–3 featured articles. These do **not** update automatically when new posts are published.

| Link text (example)                                      | Description (from article standfirst or hand-written) |
| -------------------------------------------------------- | ----------------------------------------------------- |
| EEAT for Charities: Navigating Google's Quality Guidelines | …                                                     |
| Co-Designing NHS Services: A Patient-First Framework     | …                                                     |
| Wagtail CMS in 2026: The AI-Powered Editor Experience  | …                                                     |

**Alternative:** set content source to **Manual links** for both columns if the page tree does not match the IA.

---

### 5. About

| Field               | Value                                      |
| ------------------- | ------------------------------------------ |
| Page                | About index page                           |
| Navigation text     | `About`                                    |
| Dropdown style      | **Mixed list + featured links**            |
| Content source      | **Auto-generate from page children**       |
| Page children depth | **Children only**                          |
| Secondary heading   | `About us`                                 |
| Promoted heading    | Leave blank, or use a heading if desired   |

**Prerequisites (left column — auto):**

- Child pages with **Show in menus** enabled, e.g. Careers, Culture, Team.
- **Search description** on each child for the dropdown blurb.

**Promoted links (right column — manual):**

| Link text (example)     | Typical destination              |
| ----------------------- | -------------------------------- |
| 100% Employee Owned     | Culture / ownership page         |
| Making a difference     | Impact or values page            |
| Diversity and inclusion | D&I page                         |

---

### Header CTA

In **Settings → Navigation settings → Header actions**:

| Field            | Value                          |
| ---------------- | ------------------------------ |
| Header CTA page  | Contact / Get in touch page    |
| Header CTA text  | `Get in touch`                 |

If no CTA page is set, the default contact snippet is used.

---

## Configuration checklist

Use this when setting up or reviewing Navigation settings:

- [ ] Five primary nav items in order: Sectors, Services, Work, Thinking, About
- [ ] Each item has a **Page** selected (top-level link destination)
- [ ] **Dropdown style** and **Content source** match the tables above
- [ ] **Division pages** live with search descriptions and themes (Sectors)
- [ ] **Sector** and **Service** snippets populated (Work)
- [ ] **Work index page** live (Work filter URLs)
- [ ] Thinking and About **child pages** have **Show in menus** and search descriptions
- [ ] Services, Thinking promoted, and About promoted **manual links** entered
- [ ] Header CTA page and text set
- [ ] Save settings (clears navigation fragment cache)

---

## Known limitations

| Prototype feature                         | Current behaviour                                      | Workaround                                      |
| ----------------------------------------- | ------------------------------------------------------ | ----------------------------------------------- |
| Tags on Sectors teaser cards              | Not auto-filled from division pages                    | Manual links with **tags** field                |
| Tags on Work sector rows                  | Not auto-filled from Sector snippets                   | Manual secondary links with **tags**            |
| “Latest insights” auto-updating           | Promoted links are static                              | Re-save Navigation settings when curating       |
| “Our domains” promoted column on Sectors  | Optional; no auto source                               | Manual promoted links, or leave column empty    |
| Service descriptions in Work grid         | Auto services only output name (no description in grid)| Expected for compact grid layout                |

---

## Header actions

| Field               | Purpose                                    |
| ------------------- | ------------------------------------------ |
| **Header CTA page** | Page linked from the “Get in touch” button |
| **Header CTA text** | Button label (defaults to “Get in touch”)  |

---

## Footer settings

| Field                     | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| **Footer links**          | Link list at the base of the page         |
| **Footer logos**          | Logo strip above the footer contact box   |
| **Footer newsletter CTA** | External newsletter signup link and label |

---

## Caching

Primary navigation and header actions are cached for 10 minutes. Cache is cleared automatically when navigation settings are saved.

---

## Overriding navigation text

By default the navigation displays the page title. Override this with the **Navigation text** field on primary nav items, or the **Navigation text** field under the Promote tab on individual pages.

---

## Front-end behaviour

- **Desktop**: items with children open dropdown panels on click. Escape and click-outside close open panels. The active indicator line aligns with the bottom of the header bar; dropdown panels sit below the bar.
- **Mobile**: the menu toggle opens the primary nav. Items with children drill down to a second panel with a back button and a link to the parent section.

---

## Legacy note

The old **Navigation sets** snippet and per-page “Override navigation set” field have been removed. All site IA now lives in **Settings → Navigation settings → Primary navigation**.

---

## Related code

| Concern              | Location                                              |
| -------------------- | ----------------------------------------------------- |
| Dropdown resolution  | `tbx/navigation/utils.py` → `resolve_primary_nav_dropdown` |
| Admin field definitions | `tbx/navigation/blocks.py` → `PrimaryNavLinkBlock` |
| Desktop templates    | `tbx/project_styleguide/templates/patterns/navigation/components/includes/` |
| Navigation settings  | `tbx/navigation/models.py` → `NavigationSettings`     |
