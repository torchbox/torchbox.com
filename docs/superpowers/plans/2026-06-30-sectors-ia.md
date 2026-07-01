# Sectors IA & Primary Nav Flexibility — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `SectorsIndexPage` as a parent for existing `DivisionPage` / `ServiceAreaPage`, add single-value taxonomy FKs to sector and service pages, and let primary-nav top-level items be label-only when they carry a dropdown.

**Architecture:** New `tbx/sectors` Django app holds the index page model only. `DivisionPage` and `ServiceAreaPage` stay where they are and gain a `sector` FK plus `SectorsIndexPage` as an allowed parent. `ServicePage` gains a `service` FK. Primary nav becomes more permissive in two places: the `PrimaryNavLinkBlock.clean()` rule and the `resolve_primary_nav_item` cache resolver.

**Tech Stack:** Django, Wagtail, wagtail-factories, pytest/Django test runner (matches repo conventions).

## Global Constraints

- No renames of `Division*` / `DivisionPage` identifiers.
- No data migration: existing pages stay where they are.
- `ServicePage` structure unchanged; only adds the `service` FK.
- `SectorsIndexPage` does NOT get a sector FK.
- All new FKs: nullable, `on_delete=SET_NULL`, no admin requirement.
- Template/front-end of `SectorsIndexPage` reuses `DivisionPage` template structure.
- Spec: `docs/superpowers/specs/2026-06-30-sectors-ia-design.md`.

---

## File map

**Created**

- `tbx/sectors/__init__.py`
- `tbx/sectors/apps.py`
- `tbx/sectors/models.py` — `SectorsIndexPage`
- `tbx/sectors/blocks.py` — `SectorsIndexStoryBlock` (copy of `DivisionStoryBlock`)
- `tbx/sectors/factories.py` — `SectorsIndexPageFactory` + own `DynamicHeroStreamBlockFactory` copy
- `tbx/sectors/migrations/__init__.py`
- `tbx/sectors/migrations/0001_initial.py` (generated)
- `tbx/sectors/tests/__init__.py`
- `tbx/sectors/tests/test_models.py`
- `tbx/project_styleguide/templates/patterns/pages/sectors/sectors_index_page.html` (copy of `division_page.html`)
- `tbx/project_styleguide/templates/patterns/pages/sectors/sectors_index_page.yaml` (copy of `division_page.yaml`)

**Modified**

- `tbx/settings/base.py` — register `tbx.sectors`.
- `tbx/divisions/models.py` — add `sector` FK; allow `SectorsIndexPage` as parent.
- `tbx/divisions/factories.py` — accept optional `sector`.
- `tbx/services/models.py` — `ServicePage.service` FK; `ServiceAreaPage.sector` FK; allow `SectorsIndexPage` as parent for `ServiceAreaPage`.
- `tbx/services/factories.py` — accept optional `sector` / `service`.
- `tbx/navigation/blocks.py` — `PrimaryNavLinkBlock.clean()` permits label-only items with a dropdown.
- `tbx/navigation/utils.py` — `resolve_primary_nav_item` preserves label-only items with a dropdown.
- `tbx/core/tests/test_division_mixin.py` — case: `DivisionPage` nested under `SectorsIndexPage`.
- `tbx/navigation/tests/test_nav_utils.py` — label-only resolution case.
- `tbx/divisions/tests/` and `tbx/services/tests/` — FK tests (new files if needed).

---

## Task 1: Scaffold `tbx/sectors` app and register it

**Files:**

- Create: `tbx/sectors/__init__.py`, `tbx/sectors/apps.py`, `tbx/sectors/models.py` (empty body), `tbx/sectors/migrations/__init__.py`
- Modify: `tbx/settings/base.py` (INSTALLED_APPS)

**Interfaces:**

- Produces: a registered Django app `tbx.sectors` with no models yet.

- [ ] **Step 1: Create `tbx/sectors/__init__.py` (empty file)**

- [ ] **Step 2: Create `tbx/sectors/apps.py`**

```python
from django.apps import AppConfig


class SectorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tbx.sectors"
```

- [ ] **Step 3: Create `tbx/sectors/models.py` (placeholder)**

```python
# SectorsIndexPage added in Task 2.
```

- [ ] **Step 4: Create `tbx/sectors/migrations/__init__.py` (empty file)**

- [ ] **Step 5: Register the app**

Edit `tbx/settings/base.py`. Locate the `"tbx.divisions",` line in `INSTALLED_APPS` and add `"tbx.sectors",` immediately after it (alphabetical ordering with neighbours is fine — match what's around it):

```python
    "tbx.divisions",
    "tbx.sectors",
```

- [ ] **Step 6: Sanity check — Django boots**

Run: `python manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 7: Commit**

```bash
git add tbx/sectors tbx/settings/base.py
git commit -m "Sectors: scaffold app and register in INSTALLED_APPS"
```

---

## Task 2: Add `SectorsIndexPage` model + factory + page test

**Files:**

- Modify: `tbx/sectors/models.py`
- Create: `tbx/sectors/blocks.py`, `tbx/sectors/factories.py`, `tbx/sectors/tests/__init__.py`, `tbx/sectors/tests/test_models.py`
- Create: `tbx/project_styleguide/templates/patterns/pages/sectors/sectors_index_page.html`, `tbx/project_styleguide/templates/patterns/pages/sectors/sectors_index_page.yaml`
- Generated: `tbx/sectors/migrations/0001_initial.py`

**Interfaces:**

- Produces: `SectorsIndexPage`, `SectorsIndexStoryBlock`, `SectorsIndexPageFactory`, `SectorsHeroStreamBlockFactory`.
- Consumes: `tbx.core.models.BasePage`, `tbx.core.blocks.DynamicHeroBlock`, and the same StoryBlock atoms that `tbx/divisions/blocks.py` uses.

**Note on duplication:** The user has explicitly asked for the sector index page to **own its own copies** of the division template, StreamBlock, and hero factory rather than importing them from `tbx.divisions`. Don't shortcut this with imports — copy the files so the two page types can diverge independently later.

- [ ] **Step 1: Write the failing page test**

Create `tbx/sectors/tests/__init__.py` (empty) and `tbx/sectors/tests/test_models.py`:

```python
from django.test import TestCase

from wagtail.models import Page

from tbx.sectors.factories import SectorsIndexPageFactory
from tbx.sectors.models import SectorsIndexPage


class SectorsIndexPageTests(TestCase):
    def test_can_create_under_home(self):
        home = Page.objects.get(slug="home")
        page = SectorsIndexPageFactory(parent=home, title="Sectors")
        self.assertIsInstance(page, SectorsIndexPage)
        self.assertEqual(page.get_parent().specific_class, type(home.specific))

    def test_allows_division_and_service_area_children(self):
        from tbx.divisions.models import DivisionPage
        from tbx.services.models import ServiceAreaPage

        allowed = {
            cls.__name__ for cls in SectorsIndexPage.allowed_subpage_models()
        }
        self.assertIn(DivisionPage.__name__, allowed)
        self.assertIn(ServiceAreaPage.__name__, allowed)
```

- [ ] **Step 2: Run the test to confirm it fails**

Run: `python manage.py test tbx.sectors.tests.test_models -v 2`
Expected: ImportError / no `SectorsIndexPageFactory`, or `SectorsIndexPage` does not exist.

- [ ] **Step 3: Copy the division template + yaml under a sectors path**

```bash
mkdir -p tbx/project_styleguide/templates/patterns/pages/sectors
cp tbx/project_styleguide/templates/patterns/pages/divisions/division_page.html \
   tbx/project_styleguide/templates/patterns/pages/sectors/sectors_index_page.html
cp tbx/project_styleguide/templates/patterns/pages/divisions/division_page.yaml \
   tbx/project_styleguide/templates/patterns/pages/sectors/sectors_index_page.yaml
```

Open the two copied files and update any pattern-library identifiers / titles that refer to "Division" so the styleguide entry reads as "Sectors index". Leave the HTML structure itself untouched — that's the whole point of the copy.

- [ ] **Step 4: Create `tbx/sectors/blocks.py` as a copy of `DivisionStoryBlock`**

```python
from tbx.core.blocks import (
    FeaturedServicesBlock,
    FourPhotoCollageBlock,
    IntroductionWithImagesBlock,
    LinkColumnsBlock,
    NumericStatisticsGroupBlock,
    PartnersBlock,
    StoryBlock,
    TextualStatisticsGroupBlock,
)


class SectorsIndexStoryBlock(StoryBlock):
    """
    StreamBlock used by SectorsIndexPage.

    Currently identical to tbx.divisions.blocks.DivisionStoryBlock — the
    two are deliberately kept as separate classes so the sector index
    can diverge independently as IA evolves.
    """

    four_photo_collage = FourPhotoCollageBlock()
    introduction_with_images = IntroductionWithImagesBlock()
    numeric_statistics = NumericStatisticsGroupBlock()
    textual_statistics = TextualStatisticsGroupBlock()
    partners_block = PartnersBlock()
    featured_services = FeaturedServicesBlock()
    link_columns = LinkColumnsBlock()
```

- [ ] **Step 5: Implement `SectorsIndexPage`**

Replace `tbx/sectors/models.py`:

```python
from wagtail.admin.panels import FieldPanel

from tbx.core.blocks import DynamicHeroBlock
from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField

from .blocks import SectorsIndexStoryBlock


class SectorsIndexPage(BasePage):
    """
    Umbrella landing page that lists the sectors Torchbox works in.

    Visually a sibling of DivisionPage — uses a copy of the division
    template and StreamBlock so the two page types can diverge
    independently. Children are DivisionPage and ServiceAreaPage (the
    two page types currently used as sector pages).
    """

    template = "patterns/pages/sectors/sectors_index_page.html"

    parent_page_types = ["torchbox.HomePage"]
    subpage_types = ["divisions.DivisionPage", "services.ServiceAreaPage"]

    hero = StreamField([("hero", DynamicHeroBlock())], max_num=1, min_num=1)
    body = StreamField(SectorsIndexStoryBlock(), blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("hero"),
        FieldPanel("body"),
    ]

    promote_panels = BasePage.promote_panels
```

- [ ] **Step 6: Implement the factory with its own hero stream factory**

Create `tbx/sectors/factories.py`:

```python
from wagtail import blocks

import factory
import wagtail_factories

from tbx.core.blocks import DynamicHeroBlock
from tbx.core.factories import DynamicHeroBlockFactory, StoryBlockFactory

from .models import SectorsIndexPage


class SectorsIndexHeroStreamBlock(blocks.StreamBlock):
    hero = DynamicHeroBlock()


class SectorsIndexHeroStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    class Meta:
        model = SectorsIndexHeroStreamBlock

    hero = factory.SubFactory(DynamicHeroBlockFactory)


class SectorsIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = SectorsIndexPage

    title = "Sectors"

    @factory.post_generation
    def hero(obj, create, extracted, **kwargs):
        blocks = kwargs or {"0": "hero"}
        obj.hero = SectorsIndexHeroStreamBlockFactory(**blocks)

    @factory.post_generation
    def body(obj, create, extracted, **kwargs):
        blocks = kwargs or {"0": "paragraph"}
        obj.body = StoryBlockFactory(**blocks)
```

- [ ] **Step 7: Generate the migration**

Run: `python manage.py makemigrations sectors`
Expected: creates `tbx/sectors/migrations/0001_initial.py`.

- [ ] **Step 8: Run the test, confirm it passes**

Run: `python manage.py test tbx.sectors.tests.test_models -v 2`
Expected: 2 tests pass.

- [ ] **Step 9: Commit**

```bash
git add tbx/sectors tbx/project_styleguide/templates/patterns/pages/sectors
git commit -m "Sectors: add SectorsIndexPage with copied division template, blocks, and hero factory"
```

---

## Task 3: Allow `SectorsIndexPage` as a parent for Division & ServiceArea pages

**Files:**

- Modify: `tbx/divisions/models.py` (add to `parent_page_types`)
- Modify: `tbx/services/models.py` (add to `ServiceAreaPage.parent_page_types`)

**Interfaces:**

- Consumes: `tbx.sectors.models.SectorsIndexPage`.
- Produces: editors can move/create DivisionPage and ServiceAreaPage under SectorsIndexPage in the admin.

- [ ] **Step 1: Write the failing test**

Add to `tbx/sectors/tests/test_models.py`:

```python
    def test_division_page_can_be_created_under_index(self):
        from tbx.divisions.factories import DivisionPageFactory

        home = Page.objects.get(slug="home")
        index = SectorsIndexPageFactory(parent=home, title="Sectors")
        division = DivisionPageFactory(parent=index, title="Charity")
        self.assertEqual(division.get_parent().specific, index)

    def test_service_area_page_can_be_created_under_index(self):
        from tbx.services.factories import ServiceAreaPageFactory

        home = Page.objects.get(slug="home")
        index = SectorsIndexPageFactory(parent=home, title="Sectors")
        area = ServiceAreaPageFactory(parent=index, title="GLAM")
        self.assertEqual(area.get_parent().specific, index)
```

- [ ] **Step 2: Run and confirm one (or both) fail**

Run: `python manage.py test tbx.sectors.tests.test_models -v 2`
Expected: failures due to `ServiceAreaPage` only allowing `DivisionPage` as parent (and possibly `DivisionPage` only allowing `HomePage`).

- [ ] **Step 3: Update `DivisionPage.parent_page_types`**

In `tbx/divisions/models.py`, replace:

```python
    parent_page_types = ["torchbox.HomePage"]
```

with:

```python
    parent_page_types = ["torchbox.HomePage", "sectors.SectorsIndexPage"]
```

- [ ] **Step 4: Update `ServiceAreaPage.parent_page_types`**

In `tbx/services/models.py`, replace:

```python
    parent_page_types = ["divisions.DivisionPage"]
```

with:

```python
    parent_page_types = ["divisions.DivisionPage", "sectors.SectorsIndexPage"]
```

- [ ] **Step 5: Run the tests**

Run: `python manage.py test tbx.sectors.tests.test_models -v 2`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add tbx/divisions/models.py tbx/services/models.py
git commit -m "Sectors: allow SectorsIndexPage as parent for Division and ServiceArea pages"
```

---

## Task 4: `DivisionMixin.final_division` works across a `SectorsIndexPage` ancestor

**Files:**

- Modify: `tbx/core/tests/test_division_mixin.py` (add a test case)

**Interfaces:**

- Consumes: `SectorsIndexPageFactory`, `DivisionPageFactory`, `ServiceAreaPageFactory`.

- [ ] **Step 1: Read the existing mixin and test**

Re-read `tbx/core/utils/models.py` lines around `final_division` and `tbx/core/tests/test_division_mixin.py` to find the right place to add a parametrised case.

- [ ] **Step 2: Write the failing test**

Add a new test method at the end of the appropriate class in `tbx/core/tests/test_division_mixin.py`:

```python
    def test_final_division_resolves_when_division_nested_under_sectors_index(self):
        from tbx.sectors.factories import SectorsIndexPageFactory

        sectors_index = SectorsIndexPageFactory(parent=self.home, title="Sectors")
        division = DivisionPageFactory(parent=sectors_index, title="Charity")
        service = ServiceAreaPageFactory(parent=division, title="Services")

        self.assertEqual(service.final_division, division)
```

(Imports `DivisionPageFactory` / `ServiceAreaPageFactory` are already present at the top of the file — verify.)

- [ ] **Step 3: Run, confirm it passes**

Run: `python manage.py test tbx.core.tests.test_division_mixin -v 2`
Expected: pass (no production code change needed; ancestor walk already handles intervening page types). If it FAILS, stop and investigate — the spec assumed this would just work.

- [ ] **Step 4: Commit**

```bash
git add tbx/core/tests/test_division_mixin.py
git commit -m "Division mixin: cover final_division across SectorsIndexPage ancestor"
```

---

## Task 5: Add `sector` FK to `DivisionPage`

**Files:**

- Modify: `tbx/divisions/models.py`
- Modify: `tbx/divisions/factories.py`
- Create: `tbx/divisions/tests/__init__.py` (if missing), `tbx/divisions/tests/test_models.py` (if missing)
- Generated: `tbx/divisions/migrations/00XX_division_sector.py`

**Interfaces:**

- Consumes: `tbx.taxonomy.models.Sector`.
- Produces: `DivisionPage.sector` (nullable FK).

- [ ] **Step 1: Check for existing tests dir**

Run: `ls tbx/divisions/tests/ 2>/dev/null || echo "missing"`
If missing, create `tbx/divisions/tests/__init__.py` (empty).

- [ ] **Step 2: Write the failing test**

Create or append to `tbx/divisions/tests/test_models.py`:

```python
from django.test import TestCase

from wagtail.models import Page

from tbx.divisions.factories import DivisionPageFactory
from tbx.taxonomy.factories import SectorFactory


class DivisionPageSectorTests(TestCase):
    def test_sector_can_be_assigned(self):
        sector = SectorFactory()
        home = Page.objects.get(slug="home")
        division = DivisionPageFactory(parent=home, title="Charity", sector=sector)
        division.refresh_from_db()
        self.assertEqual(division.sector, sector)

    def test_sector_is_optional(self):
        home = Page.objects.get(slug="home")
        division = DivisionPageFactory(parent=home, title="Charity")
        self.assertIsNone(division.sector)
```

(Verify `SectorFactory` exists at `tbx/taxonomy/factories.py`. If not, use `Sector.objects.create(name="X", slug="x", sort_order=0)` instead.)

- [ ] **Step 3: Run, confirm failure**

Run: `python manage.py test tbx.divisions.tests.test_models -v 2`
Expected: fail (no `sector` field).

- [ ] **Step 4: Add the field**

In `tbx/divisions/models.py`:

1. Add an import near the top: `from django.db import models` (already present — keep).
2. Add the field on `DivisionPage`, just below the `body` field:

```python
    sector = models.ForeignKey(
        "taxonomy.Sector",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="division_pages",
    )
```

3. Add a `FieldPanel` in `content_panels`, after `FieldPanel("body")`:

```python
        FieldPanel("sector"),
```

- [ ] **Step 5: Update the factory**

In `tbx/divisions/factories.py`, add a `sector` attribute on `DivisionPageFactory`:

```python
    sector = None
```

(Lets callers pass `sector=...` without affecting tests that don't.)

- [ ] **Step 6: Generate migration**

Run: `python manage.py makemigrations divisions`
Expected: a new migration `00XX_divisionpage_sector.py` is created.

- [ ] **Step 7: Run the tests**

Run: `python manage.py test tbx.divisions.tests.test_models -v 2`
Expected: pass.

- [ ] **Step 8: Commit**

```bash
git add tbx/divisions tbx/sectors/tests/test_models.py
git commit -m "Divisions: add optional sector FK on DivisionPage"
```

---

## Task 6: Add `sector` FK to `ServiceAreaPage` and `service` FK to `ServicePage`

**Files:**

- Modify: `tbx/services/models.py`
- Modify: `tbx/services/factories.py`
- Modify or create: `tbx/services/tests/test_models.py`
- Generated: `tbx/services/migrations/00XX_service_taxonomy.py`

**Interfaces:**

- Consumes: `tbx.taxonomy.models.Sector`, `tbx.taxonomy.models.Service`.
- Produces: `ServiceAreaPage.sector`, `ServicePage.service` (both nullable FKs).

- [ ] **Step 1: Write the failing tests**

In `tbx/services/tests/test_models.py` (create if absent):

```python
from django.test import TestCase

from wagtail.models import Page

from tbx.services.factories import ServiceAreaPageFactory, ServicePageFactory
from tbx.taxonomy.factories import SectorFactory, ServiceFactory


class ServiceAreaPageSectorTests(TestCase):
    def test_sector_can_be_assigned(self):
        sector = SectorFactory()
        home = Page.objects.get(slug="home")
        area = ServiceAreaPageFactory(parent=home, title="GLAM", sector=sector)
        area.refresh_from_db()
        self.assertEqual(area.sector, sector)

    def test_sector_is_optional(self):
        home = Page.objects.get(slug="home")
        area = ServiceAreaPageFactory(parent=home, title="GLAM")
        self.assertIsNone(area.sector)


class ServicePageServiceTests(TestCase):
    def test_service_can_be_assigned(self):
        service_tag = ServiceFactory()
        home = Page.objects.get(slug="home")
        page = ServicePageFactory(parent=home, title="Design", service=service_tag)
        page.refresh_from_db()
        self.assertEqual(page.service, service_tag)

    def test_service_is_optional(self):
        home = Page.objects.get(slug="home")
        page = ServicePageFactory(parent=home, title="Design")
        self.assertIsNone(page.service)
```

If `tbx/services/tests/` has no `__init__.py`, create one. Confirm `ServiceFactory` / `SectorFactory` exist in `tbx/taxonomy/factories.py`; otherwise substitute direct `.objects.create(...)` calls with `name`, `slug`, `sort_order=0`.

Note: `ServiceAreaPage` may not currently allow `HomePage` as a parent. If the test fails with a "page type not allowed" error, instead parent it under a `DivisionPage` created by `DivisionPageFactory` in `setUp`.

- [ ] **Step 2: Run, confirm failures**

Run: `python manage.py test tbx.services.tests.test_models -v 2`
Expected: fail — fields missing.

- [ ] **Step 3: Add the fields**

In `tbx/services/models.py`, add to `ServicePage` (below `body`):

```python
    service = models.ForeignKey(
        "taxonomy.Service",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_pages",
    )
```

Add `FieldPanel("service")` to `ServicePage.content_panels` after `FieldPanel("body")`.

Add to `ServiceAreaPage` (below `body`):

```python
    sector = models.ForeignKey(
        "taxonomy.Sector",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_area_pages",
    )
```

Add `FieldPanel("sector")` to `ServiceAreaPage.content_panels` after `FieldPanel("body")`.

- [ ] **Step 4: Update factories**

In `tbx/services/factories.py`, add `service = None` on `ServicePageFactory` and `sector = None` on `ServiceAreaPageFactory`.

- [ ] **Step 5: Generate migration**

Run: `python manage.py makemigrations services`
Expected: a new migration file is created.

- [ ] **Step 6: Run the tests**

Run: `python manage.py test tbx.services.tests.test_models -v 2`
Expected: pass.

- [ ] **Step 7: Commit**

```bash
git add tbx/services
git commit -m "Services: add optional sector FK on ServiceAreaPage and service FK on ServicePage"
```

---

## Task 7: `PrimaryNavLinkBlock.clean()` permits label-only items with a dropdown

**Files:**

- Modify: `tbx/navigation/blocks.py` (override `clean()` on `PrimaryNavLinkBlock`)
- Modify: `tbx/navigation/tests/test_nav_blocks.py` (create if absent) — block-level test.

**Interfaces:**

- Consumes: existing `LinkValidationMixin.clean` on `LinkBlock`.
- Produces: a `PrimaryNavLinkBlock` instance is valid when `dropdown_style != "none"`, `title` is set, and both `page` and `external_link` are blank.

- [ ] **Step 1: Find / create the block tests file**

Run: `ls tbx/navigation/tests/`
If `test_nav_blocks.py` doesn't exist, create it (and `__init__.py` if missing).

- [ ] **Step 2: Write the failing tests**

```python
from django.test import TestCase

from tbx.navigation.blocks import PrimaryNavLinkBlock


class PrimaryNavLinkBlockCleanTests(TestCase):
    def setUp(self):
        self.block = PrimaryNavLinkBlock()

    def _value(self, **overrides):
        base = {
            "page": None,
            "external_link": "",
            "title": "",
            "dropdown_style": PrimaryNavLinkBlock.DropdownStyle.NONE,
            "content_source": PrimaryNavLinkBlock.ContentSource.MANUAL,
            "main_heading": "",
            "supporting_heading": "",
            "main_links": [],
            "supporting_links": [],
            "page_children_depth": PrimaryNavLinkBlock.PageChildrenDepth.LEVEL2,
        }
        base.update(overrides)
        return self.block.to_python(base)

    def test_label_only_valid_when_dropdown_set(self):
        value = self._value(
            title="What we do",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.MIXED_LIST,
        )
        cleaned = self.block.clean(value)
        self.assertEqual(cleaned["title"], "What we do")

    def test_label_only_invalid_without_dropdown(self):
        from wagtail.blocks.struct_block import StructBlockValidationError

        value = self._value(
            title="What we do",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.NONE,
        )
        with self.assertRaises(StructBlockValidationError):
            self.block.clean(value)

    def test_label_required_when_no_link(self):
        from wagtail.blocks.struct_block import StructBlockValidationError

        value = self._value(
            title="",
            dropdown_style=PrimaryNavLinkBlock.DropdownStyle.MIXED_LIST,
        )
        with self.assertRaises(StructBlockValidationError):
            self.block.clean(value)
```

- [ ] **Step 3: Run, confirm failures**

Run: `python manage.py test tbx.navigation.tests.test_nav_blocks -v 2`
Expected: the label-only valid case fails (parent `clean()` requires a page or external link).

- [ ] **Step 4: Override `clean()` on `PrimaryNavLinkBlock`**

In `tbx/navigation/blocks.py`, on the `PrimaryNavLinkBlock` class (below the existing fields and the legacy migration helpers), add:

```python
    def clean(self, value):
        """
        Top-level nav items may be label-only headers when they carry a
        dropdown — the title opens the panel, nothing links anywhere on
        click. Without a dropdown we still need a link target, otherwise
        the item is a dead click. Title is always required.
        """
        from django.core.exceptions import ValidationError
        from django.forms.utils import ErrorList
        from wagtail.blocks.struct_block import StructBlockValidationError

        dropdown_style = value.get("dropdown_style") or self.DropdownStyle.NONE
        page = value.get("page")
        external_link = value.get("external_link")
        title = value.get("title")

        errors = {}

        if not title:
            errors["title"] = ErrorList(
                [ValidationError("A navigation label is required.")]
            )

        if dropdown_style == self.DropdownStyle.NONE:
            # Defer to the LinkBlock rule: must have exactly one of page/external_link.
            try:
                return super().clean(value)
            except StructBlockValidationError as exc:
                # Merge so a missing title plus a missing link both surface.
                for field, error in exc.block_errors.items():
                    errors[field] = error
                raise StructBlockValidationError(errors) from exc

        # dropdown present → page/external_link both optional, but
        # mutually exclusive when both supplied.
        if page and external_link:
            err = ErrorList(
                [ValidationError("You must specify either a page or an external link, not both")]
            )
            errors["page"] = err
            errors["external_link"] = err

        if errors:
            raise StructBlockValidationError(errors)

        # Use the StructBlock base clean to coerce sub-values normally,
        # bypassing LinkBlock's "must have a target" rule.
        return blocks.StructBlock.clean(self, value)
```

(Imports `blocks` already exists at the top of the file.)

- [ ] **Step 5: Run, confirm pass**

Run: `python manage.py test tbx.navigation.tests.test_nav_blocks -v 2`
Expected: all three tests pass.

- [ ] **Step 6: Commit**

```bash
git add tbx/navigation/blocks.py tbx/navigation/tests/test_nav_blocks.py
git commit -m "Primary nav: allow label-only top-level items when a dropdown is set"
```

---

## Task 8: `resolve_primary_nav_item` keeps label-only entries

**Files:**

- Modify: `tbx/navigation/utils.py`
- Modify: `tbx/navigation/tests/test_nav_utils.py`

**Interfaces:**

- Consumes: existing `PrimaryNavLinkBlock` / `NavItem` payload shape.
- Produces: `NavItem` with empty `url`, `page_id=None`, `style != NAV_STYLE_NONE` for label-only items.

- [ ] **Step 1: Write the failing test**

Append to `tbx/navigation/tests/test_nav_utils.py` (place inside an appropriate class or add a new TestCase):

```python
    def test_label_only_top_level_with_dropdown_is_kept(self):
        # Use the block directly to build a value so we exercise resolve_primary_nav_item.
        from tbx.navigation.blocks import PrimaryNavLinkBlock
        from tbx.navigation.utils import NAV_STYLE_NONE, resolve_primary_nav_item

        block = PrimaryNavLinkBlock()
        value = block.to_python(
            {
                "page": None,
                "external_link": "",
                "title": "What we do",
                "dropdown_style": PrimaryNavLinkBlock.DropdownStyle.MIXED_LIST,
                "content_source": PrimaryNavLinkBlock.ContentSource.MANUAL,
                "main_heading": "",
                "supporting_heading": "",
                "main_links": [],
                "supporting_links": [],
                "page_children_depth": PrimaryNavLinkBlock.PageChildrenDepth.LEVEL2,
            }
        )
        site = Site.objects.get(is_default_site=True)

        resolved = resolve_primary_nav_item(value, site)

        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["text"], "What we do")
        self.assertEqual(resolved["url"], "")
        self.assertIsNone(resolved["page_id"])
        self.assertNotEqual(resolved["style"], NAV_STYLE_NONE)
```

Add `from wagtail.models import Site` at the top of the file if missing.

- [ ] **Step 2: Run, confirm failure**

Run: `python manage.py test tbx.navigation.tests.test_nav_utils -v 2`
Expected: the resolver currently returns `None` because `not url` triggers the early return.

- [ ] **Step 3: Update `resolve_primary_nav_item`**

In `tbx/navigation/utils.py`, replace:

```python
    url = item.url(site=site)
    text = item.text()
    if not url or not text:
        return None
```

with:

```python
    url = item.url(site=site)
    text = item.text()
    dropdown_style = item.get("dropdown_style", NAV_STYLE_NONE)

    if not text:
        return None
    # Label-only top-level entries (no link) are valid when they carry a
    # dropdown — the title opens the panel, nothing links on click. Without
    # a dropdown an empty url means the target was deleted; drop the entry.
    if not url and dropdown_style == NAV_STYLE_NONE:
        return None
```

- [ ] **Step 4: Run, confirm pass**

Run: `python manage.py test tbx.navigation -v 2`
Expected: all navigation tests pass (existing "drop unresolved" behaviour preserved for no-dropdown entries).

- [ ] **Step 5: Bump the cache version**

In `tbx/navigation/utils.py`, increment `PRIMARY_NAV_CACHE_VERSION` by 1 (payload shape hasn't changed, but the resolver now produces entries with `url == ""` that the previous version's renderer would have dropped — safe to bump to avoid stale caches showing missing items after deploy).

```python
PRIMARY_NAV_CACHE_VERSION = 4
```

- [ ] **Step 6: Commit**

```bash
git add tbx/navigation/utils.py tbx/navigation/tests/test_nav_utils.py
git commit -m "Primary nav: keep label-only entries that carry a dropdown"
```

---

## Task 9: Confirm primary-nav template handles `url == ""` correctly

**Files:**

- Read-only review: `tbx/project_styleguide/templates/patterns/navigation/components/primary-nav.html`
- Read-only review: `tbx/project_styleguide/templates/patterns/navigation/components/primary-nav-mobile.html`

**Interfaces:** none new — verifies existing template branches.

- [ ] **Step 1: Re-read `primary-nav.html`**

Confirm that when `item.style != "none"`, the template renders a `<button>` and never references `item.url`. (At the time of writing the desktop template already does — see the top of `primary-nav.html`.)

- [ ] **Step 2: Re-read `primary-nav-mobile.html`**

Confirm the same: items with a dropdown should not produce an `<a href="">`. If the mobile template DOES use `item.url` for items with a dropdown, change that branch to render the title as a non-anchor element (e.g. `<span>` or the existing button) and add a small template-rendered test in `tbx/navigation/tests/` to assert there's no empty-href output.

- [ ] **Step 3: If a fix is needed, commit it**

```bash
git add tbx/project_styleguide/templates/patterns/navigation/components/primary-nav-mobile.html
git commit -m "Primary nav (mobile): render label-only dropdown items without empty href"
```

If no fix is needed, this task ends with no commit.

---

## Task 10: Full test run and final review

**Files:** none — verification.

- [ ] **Step 1: Run the whole suite**

Run: `python manage.py test tbx -v 1`
Expected: all tests pass. If any unrelated test breaks, investigate before claiming completion.

- [ ] **Step 2: `manage.py check`**

Run: `python manage.py check --deploy --fail-level WARNING || python manage.py check`
Expected: no new issues attributable to this change.

- [ ] **Step 3: Migrations are committed**

Run: `git status`
Expected: clean working tree, all new migration files have been committed alongside their model changes.

- [ ] **Step 4: Smoke-test in the admin (optional but recommended)**

Boot the dev server (`python manage.py runserver`), create a `SectorsIndexPage` under home, drop a `DivisionPage` and a `ServiceAreaPage` under it, tag them with sectors. Then open the Navigation settings and verify a label-only top-level item with a dropdown saves successfully.
