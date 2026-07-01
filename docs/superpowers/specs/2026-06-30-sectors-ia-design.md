# Sectors IA & Primary Nav Flexibility

**Date:** 2026-06-30
**Status:** Design — pending implementation

## Summary

Introduce a `SectorsIndexPage` as an umbrella landing page above the existing `DivisionPage` and `ServiceAreaPage`, add single-value taxonomy tagging to sector and service pages to enable future related-content surfacing, and relax primary navigation so top-level items with a dropdown can be label-only (no link target).

No renames. No content disruption. Existing `ServicePage` hierarchy is untouched structurally.

## Non-technical description

See `ia-changes-summary.txt` at the repo root.

## Scope

### In scope

- New `tbx/sectors` app containing `SectorsIndexPage`.
- Allow `DivisionPage` and `ServiceAreaPage` as children of `SectorsIndexPage`.
- Add nullable `Sector` FK to `DivisionPage` and `ServiceAreaPage`.
- Add nullable `Service` FK to `ServicePage`.
- Relax `PrimaryNavLinkBlock` to permit label-only items when a dropdown is configured.
- Update primary-nav cache builder and template to handle label-only entries.
- Tests for all of the above.

### Out of scope

- Renaming `Division` → `Sector` anywhere in code.
- Moving `DivisionPage` or `ServiceAreaPage` into the new app.
- Implementing related-content queries (the FKs are added but not consumed yet).
- Changes to `ServicePage` structure, templates, or child relationships.
- Data migration of existing `DivisionPage` / `ServiceAreaPage` content (editors will re-parent manually).

## Page model changes

### New: `tbx/sectors/models.py` — `SectorsIndexPage`

A new page model that copies the front-end of `DivisionPage` (same template structure / blocks). Starts by mirroring `DivisionPage` fields exactly; trim during implementation if any field is meaningless for an index landing.

- `parent_page_types = ["torchbox.HomePage"]` (or whatever currently allows `DivisionPage` at top level — to confirm in implementation).
- `subpage_types = ["divisions.DivisionPage", "services.ServiceAreaPage"]`.
- Reuses the division template/partials at `tbx/project_styleguide/templates/patterns/pages/divisions` (or a copy under a new sectors template dir — frontend conventions decide during implementation).
- No `Sector` FK on this model.

### `tbx/divisions/models.py` — `DivisionPage`

- Add `SectorsIndexPage` to `parent_page_types` (in addition to current allowed parents).
- Add `sector = ForeignKey("taxonomy.Sector", null=True, blank=True, on_delete=SET_NULL, related_name="division_pages")`.
- Add `FieldPanel("sector")` to the appropriate panel group.

### `tbx/services/models.py` — `ServiceAreaPage`

- Add `SectorsIndexPage` to `parent_page_types`.
- Add `sector = ForeignKey("taxonomy.Sector", null=True, blank=True, on_delete=SET_NULL, related_name="service_area_pages")`.
- Add `FieldPanel("sector")`.

### `tbx/services/models.py` — `ServicePage`

- No structural changes.
- Add `service = ForeignKey("taxonomy.Service", null=True, blank=True, on_delete=SET_NULL, related_name="service_pages")`.
- Add `FieldPanel("service")`.

### `DivisionMixin` / `final_division`

- `tbx/core/utils/models.py` traversal continues to work unchanged: it walks ancestors looking for `DivisionPage`, and `SectorsIndexPage` sitting above is just another ancestor it skips.
- A test case is added covering this scenario explicitly.

## Primary navigation changes

### `PrimaryNavLinkBlock` (`tbx/navigation/blocks.py`)

- Override `clean()` so:
  - If `dropdown_style != NONE`: page and external_link are both optional. Title is required.
  - If `dropdown_style == NONE`: existing rule stands — exactly one of page or external_link must be set.
- `LinkBlockStructValue.url()` already returns `""` when neither is set; no change needed.

### Template

- The primary-nav template renders the title as plain text (no `<a>` wrapper) when `url == ""`.
- The dropdown toggle behaviour is unchanged — clicking/hovering still opens the dropdown.

### `tbx/navigation/utils.py`

- The "drop entries whose target no longer resolves" pass (commit 94e76dd1) must skip label-only entries — they have no target to resolve, so they should be preserved unconditionally.

## Migrations

- `sectors/migrations/0001_initial.py` — creates `SectorsIndexPage`.
- `divisions/migrations/00XX_sector_fk.py` — adds `sector` FK and updates allowed parents (parent/subpage type changes only need a migration if framework-managed; otherwise class-level only).
- `services/migrations/00XX_sector_and_service_fks.py` — adds `sector` FK on `ServiceAreaPage` and `service` FK on `ServicePage`, and updates `ServiceAreaPage` allowed parents.
- No data migration. Existing pages keep current parents; editors re-parent on demand.

## Factories

- `tbx/sectors/factories.py` — `SectorsIndexPageFactory` (mirror `DivisionPageFactory`).
- `tbx/divisions/factories.py` — accept optional `sector`.
- `tbx/services/factories.py` — `ServiceAreaPageFactory` accepts optional `sector`; `ServicePageFactory` accepts optional `service`.

## Tests

### New: `tbx/sectors/tests/`

- `test_models.py`: `assertCanCreate` for `SectorsIndexPage`; allowed children include `DivisionPage` and `ServiceAreaPage`; disallowed children rejected.

### `tbx/core/tests/test_division_mixin.py`

- Add a case where `DivisionPage` is nested under `SectorsIndexPage`; assert `final_division` still resolves to the `DivisionPage`.

### `tbx/divisions/tests/` and `tbx/services/tests/`

- Sector FK / Service FK can be set and cleared; admin panel renders the field; factory accepts the argument.

### `tbx/navigation/tests/`

- Block-level: `PrimaryNavLinkBlock.clean()` allows label-only when `dropdown_style != NONE`; rejects label-only when `dropdown_style == NONE`.
- Cache: a label-only top-level entry survives the unresolved-target pass and is present in the cached structure.
- Template: label-only entry renders title as plain text, not `<a>`.

## Open questions for implementation

- Exact field set on `SectorsIndexPage` — start as a copy of `DivisionPage` fields and trim during review.
- Template location for `SectorsIndexPage` — reuse the division partials directly, or copy under a sectors path. Frontend conventions decide.
- `related_name` values for the new FKs — confirmed during implementation against any existing usage.

## Acceptance criteria

- A new `SectorsIndexPage` can be created under `HomePage` in the Wagtail admin, with `DivisionPage` and `ServiceAreaPage` as valid children.
- Existing `DivisionPage` / `ServiceAreaPage` content renders unchanged.
- `DivisionPage` and `ServiceAreaPage` editors can pick a single `Sector`; `ServicePage` editors can pick a single `Service`. All three are optional.
- A primary-nav item with a dropdown can be saved with only a title (no page, no external URL) and renders as a non-link header with its dropdown intact.
- A primary-nav item without a dropdown still requires a link target.
- All new and existing tests pass.
