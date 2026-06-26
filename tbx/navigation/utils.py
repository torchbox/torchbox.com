from typing import Any, TypedDict

from django.core.cache import cache

from tbx.divisions.models import DivisionPage
from tbx.taxonomy.models import Sector, Service
from tbx.work.models import WorkIndexPage


PRIMARY_NAV_CACHE_TIMEOUT = 3600  # 1 hour staleness backstop
# Bump when the cached payload shape changes so stale entries are bypassed.
PRIMARY_NAV_CACHE_VERSION = 3

NAV_STYLE_NONE = "none"


class NavLink(TypedDict):
    text: str
    url: str
    description: str
    tags: str
    accent_colour: str
    page_id: int | None


class NavItem(TypedDict):
    """
    A resolved primary navigation entry — self-sufficient for rendering.
    `style == NAV_STYLE_NONE` means there's no expandable panel; the
    other fields still describe the top-level link.
    """

    text: str
    url: str
    page_id: int | None
    style: str
    main_heading: str
    supporting_heading: str
    main_items: list[NavLink]
    supporting_items: list[NavLink]


def _nav_link(
    *,
    text: str,
    url: str,
    description: str = "",
    tags: str = "",
    accent_colour: str = "",
    page_id: int | None = None,
) -> NavLink:
    return NavLink(
        text=text,
        url=url,
        description=description,
        tags=tags,
        accent_colour=accent_colour,
        page_id=page_id,
    )


def format_nav_tags(tags: str) -> str:
    if not tags:
        return ""
    parts = [part.strip() for part in tags.replace("·", ",").split(",") if part.strip()]
    return " · ".join(parts)


def _primary_nav_cache_key(site_pk: int) -> str:
    # Anchored on the domain ("a site's primary navigation"), not on the
    # Python identifiers that read/write it. Site is the only natural key:
    # NavigationSettings is a BaseSiteSetting, so it's 1:1 with Site. Bump
    # PRIMARY_NAV_CACHE_VERSION when the *payload shape* changes.
    return f"navigation:primary:site-{site_pk}"


def _page_url(page, site) -> str:
    if not page:
        return ""
    return page.get_url(request=None, current_site=site) or ""


def _link_from_block(block_value, site) -> NavLink | None:
    url = block_value.url(site=site)
    if not url:
        return None

    page = block_value.get("page")
    page_id = page.pk if page else None

    return _nav_link(
        text=block_value.text(),
        url=url,
        description=block_value.get("description", ""),
        tags=format_nav_tags(block_value.get("tags", "")),
        accent_colour=block_value.get("accent_colour", ""),
        page_id=page_id,
    )


def _links_from_stream(stream, site) -> list[NavLink]:
    links = []
    for block in stream or []:
        if block.block_type != "link":
            continue
        if link := _link_from_block(block.value, site):
            links.append(link)
    return links


def _work_index_url(site) -> str | None:
    work_index = WorkIndexPage.objects.live().public().first()
    if work_index:
        return _page_url(work_index, site) or None
    return None


def _filtered_work_url(slug: str, site) -> str:
    if base_url := _work_index_url(site):
        return f"{base_url}?filter={slug}"
    return ""


def _auto_division_links(site) -> list[NavLink]:
    links = []
    for division in DivisionPage.objects.live().public().specific():
        links.append(
            _nav_link(
                text=division.nav_text,
                url=_page_url(division, site),
                description=division.search_description or "",
                accent_colour=division.theme_class or "",
                page_id=division.pk,
            )
        )
    return links


def _auto_taxonomy_sectors(site) -> list[NavLink]:
    links = []
    work_index = WorkIndexPage.objects.live().public().first()
    work_index_id = work_index.pk if work_index else None
    for sector in Sector.objects.all():
        url = _filtered_work_url(sector.slug, site)
        if not url:
            continue
        links.append(
            _nav_link(
                text=sector.name,
                url=url,
                description=sector.description,
                page_id=work_index_id,
            )
        )
    return links


def _auto_taxonomy_services(site) -> list[NavLink]:
    links = []
    work_index = WorkIndexPage.objects.live().public().first()
    work_index_id = work_index.pk if work_index else None
    for service in Service.objects.all():
        url = _filtered_work_url(service.slug, site)
        if not url:
            continue
        links.append(
            _nav_link(
                text=service.name,
                url=url,
                description=service.description,
                page_id=work_index_id,
            )
        )
    return links


def _page_child_links(page, max_depth: int, site) -> list[NavLink]:
    links = []

    def add_children(parent_page, depth: int):
        if depth > max_depth:
            return
        for child in (
            parent_page.get_children().live().public().filter(show_in_menus=True)
        ):
            specific = child.specific
            links.append(
                _nav_link(
                    text=getattr(specific, "nav_text", child.title),
                    url=_page_url(child, site),
                    description=getattr(specific, "search_description", "") or "",
                    page_id=child.pk,
                )
            )
            if depth < max_depth:
                add_children(child, depth + 1)

    add_children(page, 1)
    return links


_LEGACY_NAV_FIELDS = {
    "main_heading": "secondary_heading",
    "supporting_heading": "promoted_heading",
    "main_links": "secondary_links",
    "supporting_links": "promoted_links",
}


def _nav_field(item: Any, key: str, default: str = "") -> str:
    """Read a nav setting, falling back to legacy StreamField keys."""
    if key in item:
        return item.get(key) or default
    legacy_key = _LEGACY_NAV_FIELDS.get(key)
    if legacy_key and legacy_key in item:
        return item.get(legacy_key) or default
    return default


def _nav_stream(item: Any, key: str):
    """Read a nav link stream, falling back to legacy StreamField keys."""
    if key in item:
        return item.get(key)
    legacy_key = _LEGACY_NAV_FIELDS.get(key)
    if legacy_key:
        return item.get(legacy_key)
    return None


def _empty_panel() -> dict:
    return {
        "style": NAV_STYLE_NONE,
        "main_heading": "",
        "supporting_heading": "",
        "main_items": [],
        "supporting_items": [],
    }


def _resolve_panel(item: Any, site) -> dict:
    """Resolve the dropdown panel for a nav item.

    Returns a dict with style/headings/items. Style is NAV_STYLE_NONE when
    there's no expandable panel — empty lists for main/supporting items.
    """
    dropdown_style = item.get("dropdown_style", NAV_STYLE_NONE)
    if dropdown_style == NAV_STYLE_NONE:
        return _empty_panel()

    content_source = item.get("content_source", "manual")
    main_heading = _nav_field(item, "main_heading")
    supporting_heading = _nav_field(item, "supporting_heading")

    main_items: list[NavLink] = []
    supporting_items: list[NavLink] = []

    if content_source == "auto_divisions":
        main_items = _auto_division_links(site)
    elif content_source == "auto_taxonomy":
        main_items = _auto_taxonomy_sectors(site)
        supporting_items = _auto_taxonomy_services(site)
        if not main_heading:
            main_heading = "By sector"
        if not supporting_heading:
            supporting_heading = "By service"
    elif content_source == "page_children":
        page = item.get("page")
        if page:
            max_depth = int(item.get("page_children_depth", "2"))
            main_items = _page_child_links(page, max_depth, site)
    else:
        main_items = _links_from_stream(_nav_stream(item, "main_links"), site)

    if content_source in ("manual", "auto_divisions", "page_children"):
        supporting_items = _links_from_stream(
            _nav_stream(item, "supporting_links"), site
        )

    if not main_items and not supporting_items:
        return _empty_panel()

    return {
        "style": dropdown_style,
        "main_heading": main_heading,
        "supporting_heading": supporting_heading,
        "main_items": main_items,
        "supporting_items": supporting_items,
    }


def resolve_primary_nav_item(item: Any, site) -> NavItem:
    """
    Resolve a primary navigation block into a self-sufficient render record.

    Always returns a NavItem; entries with no expandable panel have
    style == NAV_STYLE_NONE and empty main/supporting lists.
    """
    page = item.get("page")
    return NavItem(
        text=item.text(),
        url=item.url(site=site),
        page_id=page.pk if page else None,
        **_resolve_panel(item, site),
    )


def _navigation_settings(site):
    # Local import: NavigationSettings -> utils, so we can't import at module load.
    from tbx.navigation.models import NavigationSettings

    return NavigationSettings.for_site(site)


def _build_primary_navigation(site) -> list[NavItem]:
    nav_settings = _navigation_settings(site)
    return [
        resolve_primary_nav_item(block.value, site)
        for block in nav_settings.primary_navigation
    ]


def get_primary_navigation(site) -> list[NavItem]:
    return cache.get_or_set(
        _primary_nav_cache_key(site.pk),
        lambda: _build_primary_navigation(site),
        PRIMARY_NAV_CACHE_TIMEOUT,
        version=PRIMARY_NAV_CACHE_VERSION,
    )


def invalidate_primary_nav_cache(site) -> None:
    cache.delete(
        _primary_nav_cache_key(site.pk), version=PRIMARY_NAV_CACHE_VERSION
    )


def rebuild_primary_nav_cache(site) -> list[NavItem]:
    """Force rebuild — used on NavigationSettings.save() to warm the cache."""
    resolved = _build_primary_navigation(site)
    cache.set(
        _primary_nav_cache_key(site.pk),
        resolved,
        PRIMARY_NAV_CACHE_TIMEOUT,
        version=PRIMARY_NAV_CACHE_VERSION,
    )
    return resolved


def is_current_nav_item(item: NavItem, current_page, current_url: str) -> bool:
    """Match against pre-computed current_url so we don't recompute per item."""
    if current_page is None:
        return False

    if item["page_id"] is not None and item["page_id"] == current_page.pk:
        return True

    if not item["url"] or not current_url:
        return False

    item_url = item["url"].rstrip("/")
    current = current_url.rstrip("/")
    if not item_url:
        # Item points at the site root; only the root itself is current
        # (otherwise every page would highlight the root nav entry).
        return current == ""
    return current == item_url or current.startswith(item_url + "/")
