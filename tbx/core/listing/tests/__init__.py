from wagtail.models import Site


def dropdown_tag(content: str, name: str) -> str:
    """Return the opening tag for the named filter dropdown."""
    marker = f'id="listing-filter-dropdown-{name}"'
    start = content.index(marker)
    tag_start = content.rindex("<div", 0, start)
    tag_end = content.index(">", start)
    return content[tag_start : tag_end + 1]


def reset_site_root_paths():
    """Wagtail caches `Site.get_site_root_paths()` (keyed by a fixed cache key,
    unscoped to any particular database) in whatever cache backend the project is
    configured with. In this project that's the same Redis instance dev and test
    settings both point at, so a value cached by an earlier request against a
    different database can leak into a fresh test run and make every page's `.url`
    resolve against the wrong root path (returning `None`). Clearing it before
    creating any pages guarantees it gets rebuilt from the current test database.
    """
    Site.clear_site_root_paths_cache()
