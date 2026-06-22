from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

from django.db.models import Q
from django.http import QueryDict


TAXONOMY_FILTER_PARAMS = ("sector", "service", "division")
EVENT_FILTER_PARAMS = ("timing", "type")
LEGACY_FILTER_PARAM = "filter"

# Service slugs shown in the Culture listing dropdown (UI-only split for now).
# Both groups still filter via the `service` query param. Replace with a dedicated
# taxonomy when content modelling catches up.
CULTURE_SERVICE_SLUGS = frozenset(
    {
        "culture",
        "sustainability",
        "diversity-inclusion",
        "employee-ownership",
        "eot",
    }
)


def split_service_filter_options(
    options: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Split formatted service options into main services and culture topics."""
    culture = [option for option in options if option["value"] in CULTURE_SERVICE_SLUGS]
    services = [
        option for option in options if option["value"] not in CULTURE_SERVICE_SLUGS
    ]
    return services, culture


def split_service_filter_slugs(
    slugs: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split selected service slugs into main services and culture topics."""
    culture = tuple(slug for slug in slugs if slug in CULTURE_SERVICE_SLUGS)
    services = tuple(slug for slug in slugs if slug not in CULTURE_SERVICE_SLUGS)
    return services, culture


def filter_state_for_facet(
    filter_state: TaxonomyFilterState,
    facet: str,
) -> TaxonomyFilterState:
    """Return filter state for computing one facet, excluding that facet's own values."""
    if facet == "sector":
        return TaxonomyFilterState(
            sectors=(),
            services=filter_state.services,
            divisions=filter_state.divisions,
        )
    if facet == "service":
        culture_services = tuple(
            slug for slug in filter_state.services if slug in CULTURE_SERVICE_SLUGS
        )
        return TaxonomyFilterState(
            sectors=filter_state.sectors,
            services=culture_services,
            divisions=filter_state.divisions,
        )
    if facet == "culture":
        main_services = tuple(
            slug for slug in filter_state.services if slug not in CULTURE_SERVICE_SLUGS
        )
        return TaxonomyFilterState(
            sectors=filter_state.sectors,
            services=main_services,
            divisions=filter_state.divisions,
        )
    raise ValueError(f"Unknown taxonomy facet: {facet}")


def merge_selected_filter_options(
    options: list[dict[str, str]],
    selected_slugs: tuple[str, ...],
    labels: dict[str, str],
) -> list[dict[str, str]]:
    """Keep selected slugs visible even when they have no matching results."""
    merged = {option["value"]: option for option in options}
    for slug in selected_slugs:
        if slug not in merged:
            merged[slug] = {"value": slug, "label": labels.get(slug, slug)}
    return sorted(merged.values(), key=lambda item: item["label"].lower())


@dataclass(frozen=True)
class TaxonomyFilterState:
    sectors: tuple[str, ...] = ()
    services: tuple[str, ...] = ()
    divisions: tuple[str, ...] = ()

    @classmethod
    def from_request(
        cls,
        request,
        *,
        valid_sector_slugs: set[str] | None = None,
        valid_service_slugs: set[str] | None = None,
        valid_division_slugs: set[str] | None = None,
    ) -> TaxonomyFilterState:
        sectors = _validated_slugs(
            request.GET.getlist("sector"),
            valid_sector_slugs,
        )
        services = _validated_slugs(
            request.GET.getlist("service"),
            valid_service_slugs,
        )
        divisions = _validated_slugs(
            request.GET.getlist("division"),
            valid_division_slugs,
        )

        if not sectors and not services and not divisions:
            legacy_slug = request.GET.get(LEGACY_FILTER_PARAM)
            if legacy_slug:
                sectors, services, divisions = cls._resolve_legacy_slug(
                    legacy_slug,
                    valid_sector_slugs=valid_sector_slugs,
                    valid_service_slugs=valid_service_slugs,
                    valid_division_slugs=valid_division_slugs,
                )

        return cls(sectors=sectors, services=services, divisions=divisions)

    @staticmethod
    def _resolve_legacy_slug(
        slug: str,
        *,
        valid_sector_slugs: set[str] | None,
        valid_service_slugs: set[str] | None,
        valid_division_slugs: set[str] | None,
    ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
        if valid_sector_slugs and slug in valid_sector_slugs:
            return (slug,), (), ()
        if valid_service_slugs and slug in valid_service_slugs:
            return (), (slug,), ()
        if valid_division_slugs and slug in valid_division_slugs:
            return (), (), (slug,)
        return (), (), ()

    @property
    def active_filter_count(self) -> int:
        return len(self.sectors) + len(self.services) + len(self.divisions)

    @property
    def has_filters(self) -> bool:
        return self.active_filter_count > 0

    @property
    def is_indexable(self) -> bool:
        return self.active_filter_count == 1

    def to_querydict(self, *, page: int | str | None = None) -> QueryDict:
        params: list[tuple[str, str]] = []
        for slug in self.sectors:
            params.append(("sector", slug))
        for slug in self.services:
            params.append(("service", slug))
        for slug in self.divisions:
            params.append(("division", slug))
        if page and str(page) != "1":
            params.append(("page", str(page)))
        return QueryDict(urlencode(params), mutable=True)

    def urlencode(self, *, page: int | str | None = None) -> str:
        return self.to_querydict(page=page).urlencode()

    def without(self, *, param: str, slug: str) -> TaxonomyFilterState:
        return TaxonomyFilterState(
            sectors=tuple(
                s for s in self.sectors if not (param == "sector" and s == slug)
            ),
            services=tuple(
                s for s in self.services if not (param == "service" and s == slug)
            ),
            divisions=tuple(
                s for s in self.divisions if not (param == "division" and s == slug)
            ),
        )

    def selected_labels(
        self,
        *,
        sector_labels: dict[str, str],
        service_labels: dict[str, str],
        division_labels: dict[str, str],
    ) -> list[tuple[str, str, str]]:
        """Return (param_name, slug, label) tuples in display order."""
        selected: list[tuple[str, str, str]] = []
        for slug in self.sectors:
            selected.append(("sector", slug, sector_labels.get(slug, slug)))
        for slug in self.services:
            selected.append(("service", slug, service_labels.get(slug, slug)))
        for slug in self.divisions:
            selected.append(("division", slug, division_labels.get(slug, slug)))
        return selected


@dataclass(frozen=True)
class EventFilterState:
    timing: str | None = None
    types: tuple[str, ...] = ()

    @classmethod
    def from_request(
        cls,
        request,
        *,
        valid_type_slugs: set[str] | None = None,
    ) -> EventFilterState:
        timing_values = request.GET.getlist("timing")
        timing = timing_values[0] if timing_values else None
        if timing not in {"upcoming", "past"}:
            legacy_filter = request.GET.get(LEGACY_FILTER_PARAM)
            if legacy_filter in {"upcoming", "past"}:
                timing = legacy_filter
            elif timing_values:
                timing = None
            else:
                timing = None

        types = _validated_slugs(request.GET.getlist("type"), valid_type_slugs)
        return cls(timing=timing, types=types)

    @property
    def active_filter_count(self) -> int:
        count = len(self.types)
        if self.timing:
            count += 1
        return count

    @property
    def has_filters(self) -> bool:
        return self.active_filter_count > 0

    @property
    def is_indexable(self) -> bool:
        return self.active_filter_count == 1

    def to_querydict(self, *, page: int | str | None = None) -> QueryDict:
        params: list[tuple[str, str]] = []
        if self.timing:
            params.append(("timing", self.timing))
        for slug in self.types:
            params.append(("type", slug))
        if page and str(page) != "1":
            params.append(("page", str(page)))
        return QueryDict(urlencode(params), mutable=True)

    def urlencode(self, *, page: int | str | None = None) -> str:
        return self.to_querydict(page=page).urlencode()

    def without(self, *, param: str, slug: str | None = None) -> EventFilterState:
        if param == "timing":
            return EventFilterState(timing=None, types=self.types)
        return EventFilterState(
            timing=self.timing,
            types=tuple(s for s in self.types if s != slug),
        )

    def selected_labels(
        self,
        *,
        type_labels: dict[str, str],
        timing_labels: dict[str, str],
    ) -> list[tuple[str, str, str]]:
        selected: list[tuple[str, str, str]] = []
        if self.timing and self.timing in timing_labels:
            selected.append(("timing", self.timing, timing_labels[self.timing]))
        for slug in self.types:
            selected.append(("type", slug, type_labels[slug]))
        return selected


def _validated_slugs(
    slugs: list[str],
    valid_slugs: set[str] | None,
) -> tuple[str, ...]:
    if not slugs:
        return ()
    if valid_slugs is None:
        return tuple(dict.fromkeys(slugs))
    return tuple(dict.fromkeys(slug for slug in slugs if slug in valid_slugs))


def apply_taxonomy_filters(queryset, filter_state: TaxonomyFilterState):
    if filter_state.sectors:
        queryset = queryset.filter(related_sectors__slug__in=filter_state.sectors)
    if filter_state.services:
        queryset = queryset.filter(related_services__slug__in=filter_state.services)
    if filter_state.divisions:
        queryset = _apply_division_filter(queryset, filter_state.divisions)
    return queryset.distinct()


def apply_work_page_filters(queryset, filter_state: TaxonomyFilterState):
    if filter_state.sectors:
        queryset = queryset.filter(
            Q(workpage__related_sectors__slug__in=filter_state.sectors)
            | Q(historicalworkpage__related_sectors__slug__in=filter_state.sectors)
        )
    if filter_state.services:
        queryset = queryset.filter(
            Q(workpage__related_services__slug__in=filter_state.services)
            | Q(historicalworkpage__related_services__slug__in=filter_state.services)
        )
    if filter_state.divisions:
        queryset = _apply_page_division_filter(queryset, filter_state.divisions)
    return queryset.distinct()


def _apply_division_filter(queryset, division_slugs: tuple[str, ...]):
    from tbx.divisions.models import DivisionPage

    division_paths = list(
        DivisionPage.objects.filter(slug__in=division_slugs).values_list(
            "path", flat=True
        )
    )
    if not division_paths:
        return queryset.none()

    path_query = Q()
    for path in division_paths:
        path_query |= Q(path__startswith=path)
    return queryset.filter(path_query | Q(division__slug__in=division_slugs))


def _apply_page_division_filter(queryset, division_slugs: tuple[str, ...]):
    from tbx.divisions.models import DivisionPage

    division_paths = list(
        DivisionPage.objects.filter(slug__in=division_slugs).values_list(
            "path", flat=True
        )
    )
    if not division_paths:
        return queryset.none()

    path_query = Q()
    for path in division_paths:
        path_query |= Q(path__startswith=path)
    return queryset.filter(
        path_query
        | Q(workpage__division__slug__in=division_slugs)
        | Q(historicalworkpage__division__slug__in=division_slugs)
        | Q(division__slug__in=division_slugs)
    )


def paginate_queryset(queryset_or_list, page_number, per_page: int = 10):
    from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

    paginator = Paginator(queryset_or_list, per_page)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def build_listing_seo_context(
    *,
    page_title: str,
    filter_labels: list[str],
    active_filter_count: int,
    base_url: str,
    current_url: str,
    has_page_param: bool,
) -> dict:
    document_title = page_title
    if len(filter_labels) == 1:
        document_title = f"{page_title} filtered by {filter_labels[0]}"
    elif len(filter_labels) > 1:
        document_title = f"{page_title} filtered by {', '.join(filter_labels)}"

    robots_content = None
    if active_filter_count > 1:
        robots_content = "noindex, nofollow"

    canonical_url = None
    if active_filter_count == 0 and has_page_param:
        canonical_url = base_url
    elif active_filter_count == 1:
        canonical_url = current_url
    elif active_filter_count > 1:
        canonical_url = base_url

    return {
        "listing_document_title": document_title,
        "listing_robots_content": robots_content,
        "listing_canonical_url": canonical_url,
    }


def build_filter_remove_url(
    base_url: str,
    filter_state: TaxonomyFilterState | EventFilterState,
    *,
    param: str,
    slug: str | None = None,
) -> str:
    updated = filter_state.without(param=param, slug=slug)
    query = updated.urlencode()
    if query:
        return f"{base_url}?{query}"
    return base_url


def build_clear_filters_url(base_url: str) -> str:
    return base_url


def get_listing_paths(page, request) -> tuple[str, str]:
    """Return (relative_path, absolute_url) for the listing page."""
    listing_path = page.get_url(request)
    absolute_url = request.build_absolute_uri(listing_path)
    return listing_path, absolute_url
