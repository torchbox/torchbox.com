from dataclasses import dataclass
from typing import Any

from django.core.cache import cache

from tbx.divisions.models import DivisionPage
from tbx.taxonomy.models import Sector, Service
from tbx.work.models import WorkIndexPage

PRIMARY_NAV_CACHE_TIMEOUT = 3600  # 1 hour staleness backstop


@dataclass(frozen=True)
class ResolvedNavLink:
    text: str
    url: str
    description: str = ""
    tags: str = ""
    accent_colour: str = ""
    page_id: int | None = None


def format_nav_tags(tags: str) -> str:
    if not tags:
        return ""
    parts = [part.strip() for part in tags.replace("·", ",").split(",") if part.strip()]
    return " · ".join(parts)


def _primary_nav_cache_key(nav_settings_pk: int, site_pk: int) -> str:
    return f"primary_nav_dropdowns:{nav_settings_pk}:{site_pk}"


def _page_url(page, site) -> str:
    if not page:
        return ""
    return page.get_url(request=None, current_site=site) or ""


def _nav_item_url(item, site) -> str:
    page = item.get("page")
    if page:
        return _page_url(page, site)
    return item.get("external_link") or ""


def _link_from_block(block_value, site) -> ResolvedNavLink | None:
    page = block_value.get("page")
    if page:
        url = _page_url(page, site)
        page_id = page.pk
    elif external_link := block_value.get("external_link"):
        url = external_link
        page_id = None
    else:
        return None

    if not url:
        return None

    return ResolvedNavLink(
        text=block_value.text(),
        url=url,
        description=block_value.get("description", ""),
        tags=format_nav_tags(block_value.get("tags", "")),
        accent_colour=block_value.get("accent_colour", ""),
        page_id=page_id,
    )


def _links_from_stream(stream, site) -> list[ResolvedNavLink]:
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


def _auto_division_links(site) -> list[ResolvedNavLink]:
    links = []
    for division in DivisionPage.objects.live().public().specific():
        links.append(
            ResolvedNavLink(
                text=division.nav_text,
                url=_page_url(division, site),
                description=division.search_description or "",
                accent_colour=division.theme_class or "",
                page_id=division.pk,
            )
        )
    return links


def _auto_taxonomy_sectors(site) -> list[ResolvedNavLink]:
    links = []
    work_index = WorkIndexPage.objects.live().public().first()
    work_index_id = work_index.pk if work_index else None
    for sector in Sector.objects.all():
        url = _filtered_work_url(sector.slug, site)
        if not url:
            continue
        links.append(
            ResolvedNavLink(
                text=sector.name,
                url=url,
                description=sector.description,
                page_id=work_index_id,
            )
        )
    return links


def _auto_taxonomy_services(site) -> list[ResolvedNavLink]:
    links = []
    work_index = WorkIndexPage.objects.live().public().first()
    work_index_id = work_index.pk if work_index else None
    for service in Service.objects.all():
        url = _filtered_work_url(service.slug, site)
        if not url:
            continue
        links.append(
            ResolvedNavLink(
                text=service.name,
                url=url,
                description=service.description,
                page_id=work_index_id,
            )
        )
    return links


def _page_child_links(page, max_depth: int, site) -> list[ResolvedNavLink]:
    links = []

    def add_children(parent_page, depth: int):
        if depth > max_depth:
            return
        for child in (
            parent_page.get_children().live().public().filter(show_in_menus=True)
        ):
            specific = child.specific
            links.append(
                ResolvedNavLink(
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


def resolve_primary_nav_dropdown(item: Any, site) -> dict | None:
    """
    Resolve dropdown content for a primary navigation item.

    Returns None when the item has no dropdown, otherwise a dict with layout
    metadata and resolved link lists for templates.
    """
    dropdown_style = item.get("dropdown_style", "none")
    if dropdown_style == "none":
        return None

    content_source = item.get("content_source", "manual")
    main_heading = _nav_field(item, "main_heading")
    supporting_heading = _nav_field(item, "supporting_heading")

    main_items: list[ResolvedNavLink] = []
    supporting_items: list[ResolvedNavLink] = []

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
        return None

    return {
        "style": dropdown_style,
        "main_heading": main_heading,
        "supporting_heading": supporting_heading,
        "main_items": main_items,
        "supporting_items": supporting_items,
        "parent_url": _nav_item_url(item, site),
        "parent_text": item.text(),
    }


def rebuild_primary_nav_cache(nav_settings, site) -> list[dict | None]:
    dropdowns = [
        resolve_primary_nav_dropdown(block.value, site)
        for block in nav_settings.primary_navigation
    ]
    cache.set(
        _primary_nav_cache_key(nav_settings.pk, site.pk),
        dropdowns,
        PRIMARY_NAV_CACHE_TIMEOUT,
    )
    return dropdowns


def get_primary_nav_dropdowns(nav_settings, site) -> list[dict | None]:
    key = _primary_nav_cache_key(nav_settings.pk, site.pk)
    dropdowns = cache.get(key)
    nav_item_count = len(nav_settings.primary_navigation)

    if dropdowns is None or len(dropdowns) != nav_item_count:
        return rebuild_primary_nav_cache(nav_settings, site)

    return dropdowns


def item_has_dropdown(item: Any, site) -> bool:
    if item.get("dropdown_style", "none") == "none":
        return False
    return resolve_primary_nav_dropdown(item, site) is not None


def _page_url_for_current_check(page, site) -> str:
    if hasattr(page, "get_url"):
        return page.get_url(request=None, current_site=site) or ""
    return getattr(page, "url", None) or ""


def primary_nav_item_is_current(item: Any, current_page, site) -> bool:
    page = item.get("page")
    if not page or current_page is None:
        return False

    if current_page.pk == page.pk:
        return True

    page_url = _page_url_for_current_check(page, site)
    current_url = _page_url_for_current_check(current_page, site)
    if not page_url or not current_url:
        return False

    page_url = page_url.rstrip("/")
    current_url = current_url.rstrip("/")
    return current_url.startswith(page_url + "/")
