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

**Last checked** Wagtail 6.4 upgrade

- wagtail-accessibility
- [wagtail-lite-youtube-embed](front-end/lite-youtube.md)
- [wagtail-markdown](front-end/markdown-codehilite.md)
- wagtailmedia
- wagtail-purge

## Custom wagtail admin templates

**Last checked** Wagtail 6.4 upgrade

Wagtail core is expected to see an update to prevent the preview panel from scroll at every content update. To prevent this from happening until then, fix has been applied to the `sueryder/project_styleguide/templates/patterns/base.html` template.

Further information is available in a MR for Wagtail Kit: https://git.torchbox.com/internal/wagtail-kit/-/merge_requests/973
