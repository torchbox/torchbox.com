# Upgrading guidelines

This document describes aspects of the system which should be given particular attention when upgrading Wagtail or its dependencies.

## Critical paths

The following areas of functionality are critical paths for the site which don't have full automated tests and should be checked manually.

### 1. Content Management

- **Creating, editing, and publishing pages**: Test the functionality of creating new pages, editing existing content, and publishing changes.
- **Content organization and navigation**: Verify that the site's content hierarchy and navigation structure are maintained correctly after the upgrade. See also the [docs on the navigation](navigation.md).
- **Media management**: Check the uploading, storage, and retrieval of media files, such as images and documents.

### 2. Templates and Styling

- **Front-end templates**: Test the rendering of templates to ensure they display as expected after the upgrade.
- **Styling and CSS**: Check that the site's stylesheets and design elements are correctly applied and maintained.

### 3. Performance and Caching

- **Page loading speed**: Monitor the site's performance and loading times to ensure the upgrade doesn't introduce any significant slowdowns.
- **Caching mechanisms**: Verify that caching mechanisms, such as page caching and database caching, are working correctly.

## Other considerations

As well as testing the critical paths, these areas of functionality should be checked:

### General

- Other places where you know extra maintenance or checks may be necessary
- This could be code which you know should be checked and possibly removed - e.g. because you've patched something until a fix is merged in a subsequent release.
- Any previous fixes which may need to be updated/reapplied on subsequent upgrades
- Technical debt which could be affected by an upgrade.

### Custom StreamField

As indicated [here](./custom-features/migration-friendly-streamfields.md), this project uses a custom field class (`tbx.core.utils.fields.StreamField`) instead of the usual `wagtail.fields.StreamField` field for streamfield content.

### Page themes

- Ensure that the [page themes](custom-features/theme.md) are still working correctly

### Dark and light mode

- Ensure that [light and dark mode](custom-features/modes.md) are still working correctly

#### Lite youtube integration

- Check that the [custom lite youtube](front-end/lite-youtube.md) feature is still working for all youtube embeds

#### Code blocks using wagtail-markdown

- Check that [code blocks](front-end/markdown-codehilite.md) still display as expected

### Responsive images

- The [responsive images](front-end/responsive-images.md) (`{% srcset_image %}` and `<picture>` tags) can use a lot of memory if renditions need to be recreated. Consider any changes that force image renditions to be recreated out of UK working hours, and visit the work listing, blog listing and team pages to force the new renditions to be created.

### Contact snippets in footer

- Ensure that these still display all the relevant content - title, text, photo, role contact link, button text and email text

## Wagtail package dependencies

We are maintaining our own forks of Wagtail packages at: <https://github.com/torchbox-forks>.

The enables any team member to propose a change to a package, we can all work directly on the work branch and submit it to the original author for consideration.

- [How we work on forked packages (intranet article).](https://intranet.torchbox.com/torchbox-teams/tech-team/working-with-3rd-party-packages/#forking-repositories)
- [Where we manage forked packages (Monday board).](https://torchbox.monday.com/boards/1124794299)

As much as possible, we want to use the official releases available on PyPI for the Wagtail package dependencies. A temporary solution is to fork the package dependency, tag the working branch, and use the tag in the pyproject file.

### Check these packages for updates

**Last checked** Wagtail 7.3 upgrade

- wagtail-accessibility
- [wagtail-lite-youtube-embed](front-end/lite-youtube.md)
- [wagtail-markdown](front-end/markdown-codehilite.md)
- wagtailmedia
- wagtail-purge

## Custom wagtail admin templates

**Last checked** Wagtail 7.3 upgrade

Add references to any custom templates that override the Wagtail admin templates. These should be checked to ensure they still work as expected after the upgrade.

## Node dependency holds

### typescript held at `^6.0.3` (< 7)

**Instated:** 2026-09-01 (TWE-728 Node bump)

`ncu` advanced `typescript` to `7.0.2`, but `ts-jest@29.4.12` (the latest published release) declares `peerDependencies.typescript: ">=4.3 <7"`, so a clean-state install fails:

```
npm error ERESOLVE unable to resolve dependency tree
npm error peer typescript@">=4.3 <7" from ts-jest@29.4.12
```

There is no newer `ts-jest` release that supports TypeScript 7 (checked all published versions up to 29.4.12). `typescript` is held at `^6.0.3` (the latest 6.x) until `ts-jest` ships a release with a `typescript: ">=7"`-compatible peer range.

**Lift condition:** re-check `ts-jest`'s peer range each cycle; lift once it supports TypeScript 7.

### ESLint ceiling (global, not project-specific)

`eslint` and `eslint-webpack-plugin` are held at `^8.57.1` / `^5.0.3` — the range `eslint-config-torchbox@^1.1.0` supports. `eslint-config-torchbox` has not yet published a flat-config (ESLint v9) release; see the [ESLint v9 migration guide](https://eslint.org/docs/latest/use/migrate-to-9.0.0) for what that release will need to adopt. This is the standard, global ESLint v8→v9 ceiling enforced automatically by the Node bump tooling; it lifts only via the ESLint→Biome migration, not a per-project decision.

### Tailwind CSS `@config` fallback

Last checked on Wagtail 8.0

`tailwind.config.js` is loaded via the v4 `@config` fallback (from `tbx/static_src/css/tailwind.css`) rather than translated to a CSS `@theme` block, because `theme.colors` is not a flat translatable map: two token names are camelCase (`offBlack`, `themePrimary`), which can't survive as v4 CSS custom-property tokens, and several values reference CSS custom properties (`var(--color--background)`, `var(--color--heading)`, `var(--color--theme-primary)`) that need a value-preserving translation, not a mechanical copy. Moving to `@theme` needs a hand-authored token rewrite — renaming the camelCase tokens everywhere they're used as classes, and re-expressing the `var(--color--…)` values as v4 theme values — a design-token effort rather than a mechanical migration.

Tailwind is kept in its own plain-CSS entry (`tbx/static_src/css/tailwind.css`, imported directly from `main.js`) rather than folded into the Sass entry (`main.scss`): Dart Sass hoists `@import` to the top of its output, which would separate `@import 'tailwindcss'` from the adjacent `@config` directive and stop `@tailwindcss/postcss` generating utilities. Don't merge it into `main.scss` to "simplify" the entry points.
