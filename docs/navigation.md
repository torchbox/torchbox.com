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

### Dropdown styles

| Style                           | Best for                        | Renders                                                                     |
| ------------------------------- | ------------------------------- | --------------------------------------------------------------------------- |
| **Teaser grid / card list**     | Division pages, visual cards    | Main column as a card grid; promoted column as a featured list when present |
| **Mixed list + featured links** | Services, Thinking, About       | Two-column list with descriptions                                           |
| **Taxonomy index**              | Work filtered by sector/service | Sector list + compact service grid                                          |
| **No dropdown**                 | Simple top-level links          | Plain header link                                                           |

On mobile, all dropdown styles use the same drill-down panel (flat list with optional promoted section).

### Content sources

| Source                                 | Populates                                                                                                                                        |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Manual links**                       | Secondary and promoted link streams edited below                                                                                                 |
| **Auto-generate from division pages**  | All live division pages (uses nav text, search description, theme)                                                                               |
| **Auto-generate sectors and services** | Sectors in the main column, services in the promoted column (links to work index with `?filter=`). Default headings: “By sector” / “By service”. |
| **Auto-generate from page children**   | Children (and optionally grandchildren) of the selected page with “Show in menus” enabled                                                        |

If a dropdown style is set but no links can be resolved, the item renders as a plain link (no chevron).

### Suggested configuration

| Item     | Dropdown style              | Content source                     |
| -------- | --------------------------- | ---------------------------------- |
| Sectors  | Teaser grid                 | Auto-generate from division pages  |
| Services | Mixed list + featured links | Manual                             |
| Work     | Taxonomy index              | Auto-generate sectors and services |
| Thinking | Mixed list + featured links | Manual                             |
| About    | Mixed list + featured links | Manual                             |

## Header actions

| Field               | Purpose                                    |
| ------------------- | ------------------------------------------ |
| **Header CTA page** | Page linked from the “Get in touch” button |
| **Header CTA text** | Button label (defaults to “Get in touch”)  |

If no CTA page is set, the default contact snippet is used.

## Footer settings

| Field                     | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| **Footer links**          | Link list at the base of the page         |
| **Footer logos**          | Logo strip above the footer contact box   |
| **Footer newsletter CTA** | External newsletter signup link and label |

## Caching

Primary navigation and header actions are cached for 10 minutes. Cache is cleared automatically when navigation settings are saved.

## Overriding navigation text

By default the navigation displays the page title. Override this with the “Navigation text” field on primary nav items, or the navigation text field under the Promote tab on individual pages.

## Front-end behaviour

- **Desktop**: items with children open dropdown panels on click. Escape and click-outside close open panels.
- **Mobile**: the menu toggle opens the primary nav. Items with children drill down to a second panel with a back button and a link to the parent section.

## Legacy note

The old **Navigation sets** snippet and per-page “Override navigation set” field have been removed. All site IA now lives in **Settings → Navigation settings → Primary navigation**.
