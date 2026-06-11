from dataclasses import dataclass
from typing import Any

from tbx.divisions.models import DivisionPage
from tbx.taxonomy.models import Sector, Service
from tbx.work.models import WorkIndexPage


@dataclass(frozen=True)
class ResolvedNavLink:
    text: str
    url: str
    description: str = ""
    tags: str = ""
    accent_colour: str = ""


def format_nav_tags(tags: str) -> str:
    if not tags:
        return ""
    parts = [part.strip() for part in tags.replace("·", ",").split(",") if part.strip()]
    return " · ".join(parts)


def _link_from_block(block_value) -> ResolvedNavLink | None:
    url = block_value.url()
    if not url:
        return None

    return ResolvedNavLink(
        text=block_value.text(),
        url=url,
        description=block_value.get("description", ""),
        tags=format_nav_tags(block_value.get("tags", "")),
        accent_colour=block_value.get("accent_colour", ""),
    )


def _links_from_stream(stream) -> list[ResolvedNavLink]:
    links = []
    for block in stream or []:
        if block.block_type != "link":
            continue
        if link := _link_from_block(block.value):
            links.append(link)
    return links


def _work_index_url() -> str | None:
    work_index = WorkIndexPage.objects.live().public().first()
    if work_index:
        return work_index.url
    return None


def _filtered_work_url(slug: str) -> str:
    if base_url := _work_index_url():
        return f"{base_url}?filter={slug}"
    return ""


def _auto_division_links() -> list[ResolvedNavLink]:
    links = []
    for division in DivisionPage.objects.live().public().specific():
        links.append(
            ResolvedNavLink(
                text=division.nav_text,
                url=division.url,
                description=division.search_description or "",
                accent_colour=division.theme_class or "",
            )
        )
    return links


def _auto_taxonomy_sectors() -> list[ResolvedNavLink]:
    links = []
    for sector in Sector.objects.all():
        url = _filtered_work_url(sector.slug)
        if not url:
            continue
        links.append(
            ResolvedNavLink(
                text=sector.name,
                url=url,
                description=sector.description,
            )
        )
    return links


def _auto_taxonomy_services() -> list[ResolvedNavLink]:
    links = []
    for service in Service.objects.all():
        url = _filtered_work_url(service.slug)
        if not url:
            continue
        links.append(
            ResolvedNavLink(
                text=service.name,
                url=url,
                description=service.description,
            )
        )
    return links


def _page_child_links(page, max_depth: int) -> list[ResolvedNavLink]:
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
                    url=child.url,
                    description=getattr(specific, "search_description", "") or "",
                )
            )
            if depth < max_depth:
                add_children(child, depth + 1)

    add_children(page, 1)
    return links


def resolve_primary_nav_dropdown(item: Any) -> dict | None:
    """
    Resolve dropdown content for a primary navigation item.

    Returns None when the item has no dropdown, otherwise a dict with layout
    metadata and resolved link lists for templates.
    """
    dropdown_style = item.get("dropdown_style", "none")
    if dropdown_style == "none":
        return None

    content_source = item.get("content_source", "manual")
    secondary_heading = item.get("secondary_heading", "")
    promoted_heading = item.get("promoted_heading", "")

    secondary_items: list[ResolvedNavLink] = []
    promoted_items: list[ResolvedNavLink] = []

    if content_source == "auto_divisions":
        secondary_items = _auto_division_links()
    elif content_source == "auto_taxonomy":
        secondary_items = _auto_taxonomy_sectors()
        promoted_items = _auto_taxonomy_services()
        if not secondary_heading:
            secondary_heading = "By sector"
        if not promoted_heading:
            promoted_heading = "By service"
    elif content_source == "page_children":
        page = item.get("page")
        if page:
            max_depth = int(item.get("page_children_depth", "2"))
            secondary_items = _page_child_links(page, max_depth)
    else:
        secondary_items = _links_from_stream(item.get("secondary_links"))
        promoted_items = _links_from_stream(item.get("promoted_links"))

    if not secondary_items and not promoted_items:
        return None

    return {
        "style": dropdown_style,
        "secondary_heading": secondary_heading,
        "promoted_heading": promoted_heading,
        "secondary_items": secondary_items,
        "promoted_items": promoted_items,
        "parent_url": item.url(),
        "parent_text": item.text(),
    }


def item_has_dropdown(item: Any) -> bool:
    if item.get("dropdown_style", "none") == "none":
        return False
    return resolve_primary_nav_dropdown(item) is not None


def primary_nav_item_is_current(item: Any, current_page) -> bool:
    page = item.get("page")
    if not page or current_page is None:
        return False

    if current_page.pk == page.pk:
        return True

    page_url = page.url.rstrip("/")
    current_url = current_page.url.rstrip("/")
    return current_url.startswith(page_url + "/")
