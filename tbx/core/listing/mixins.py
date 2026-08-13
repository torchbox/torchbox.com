from __future__ import annotations

from dataclasses import dataclass

from tbx.core.listing.filters import (
    CULTURE_SERVICE_SLUGS,
    DROPDOWN_LABELS,
    TaxonomyFilterState,
    apply_taxonomy_filters,
    apply_work_page_filters,
    build_listing_urls_context,
    build_selected_filter_items,
    dropdown_is_visible,
    filter_state_for_facet,
    merge_selected_filter_options,
    paginate_queryset,
    split_service_filter_options,
    split_service_filter_slugs,
)
from tbx.divisions.models import DivisionPage
from tbx.taxonomy.models import Sector, Service


@dataclass(frozen=True)
class TaxonomyListingFilters:
    """Everything the taxonomy filter UI needs for one request."""

    options: dict[str, list[dict[str, str]]]
    visibility: dict[str, bool]
    sector_labels: dict[str, str]
    service_labels: dict[str, str]


def _format_filter_options(queryset, *, label_attr: str) -> list[dict[str, str]]:
    return [
        {"value": item.slug, "label": getattr(item, label_attr)} for item in queryset
    ]


def build_taxonomy_listing_filters(
    *,
    base_queryset,
    filter_state: TaxonomyFilterState,
    apply_filters,
    get_used_sectors,
    get_used_services,
    selection_labels: dict[str, dict[str, str]],
) -> TaxonomyListingFilters:
    """Build the dropdown options and visibility for a taxonomy listing.

    Options are faceted — narrowed by the *other* active filters — while visibility is
    decided from the unfiltered listing so dropdowns don't come and go as filters are
    applied. When nothing is selected those two are the same thing, so the baseline is
    only computed a second time when there is actually a filter active.
    """
    options, sector_labels, service_labels = _facet_options(
        base_queryset=base_queryset,
        filter_state=filter_state,
        apply_filters=apply_filters,
        get_used_sectors=get_used_sectors,
        get_used_services=get_used_services,
        selection_labels=selection_labels,
    )

    baseline_options = options
    if filter_state.has_filters:
        baseline_options, _, _ = _facet_options(
            base_queryset=base_queryset,
            filter_state=TaxonomyFilterState(),
            apply_filters=apply_filters,
            get_used_sectors=get_used_sectors,
            get_used_services=get_used_services,
            selection_labels={},
        )

    selected_services, selected_culture = split_service_filter_slugs(
        filter_state.services
    )
    visibility = {
        "sector": dropdown_is_visible(
            baseline_options["sectors"], filter_state.sectors, DROPDOWN_LABELS["sector"]
        ),
        "service": dropdown_is_visible(
            baseline_options["services"], selected_services, DROPDOWN_LABELS["service"]
        ),
        "culture": dropdown_is_visible(
            baseline_options["culture"], selected_culture, DROPDOWN_LABELS["culture"]
        ),
    }

    return TaxonomyListingFilters(
        options=options,
        visibility=visibility,
        sector_labels=sector_labels,
        service_labels=service_labels,
    )


def _facet_options(
    *,
    base_queryset,
    filter_state: TaxonomyFilterState,
    apply_filters,
    get_used_sectors,
    get_used_services,
    selection_labels: dict[str, dict[str, str]],
) -> tuple[dict[str, list[dict[str, str]]], dict[str, str], dict[str, str]]:
    sectors = get_used_sectors(
        apply_filters(base_queryset, filter_state_for_facet(filter_state, "sector"))
    )
    services = get_used_services(
        apply_filters(base_queryset, filter_state_for_facet(filter_state, "service"))
    )
    culture_services = get_used_services(
        apply_filters(base_queryset, filter_state_for_facet(filter_state, "culture"))
    )

    selected_services, selected_culture = split_service_filter_slugs(
        filter_state.services
    )

    sector_labels = {
        **{sector.slug: sector.name for sector in sectors},
        **selection_labels.get("sector", {}),
    }
    service_labels = {
        **{service.slug: service.name for service in services},
        **{service.slug: service.name for service in culture_services},
        **selection_labels.get("service", {}),
    }

    options = {
        "sectors": merge_selected_filter_options(
            _format_filter_options(sectors, label_attr="name"),
            filter_state.sectors,
            sector_labels,
        ),
        "services": merge_selected_filter_options(
            split_service_filter_options(
                _format_filter_options(services, label_attr="name")
            )[0],
            selected_services,
            service_labels,
        ),
        "culture": merge_selected_filter_options(
            split_service_filter_options(
                _format_filter_options(culture_services, label_attr="name")
            )[1],
            selected_culture,
            service_labels,
        ),
    }
    return options, sector_labels, service_labels


def _selected_service_filters(
    filter_state: TaxonomyFilterState,
) -> dict[str, tuple[str, ...]]:
    selected_services, selected_culture = split_service_filter_slugs(
        filter_state.services
    )
    return {
        "selected_services": selected_services,
        "selected_culture": selected_culture,
    }


class HtmxListingMixin:
    partial_template_name = "patterns/pages/listing/listing_panel_partial.html"

    def get_template(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return self.partial_template_name
        return self.template


class TaxonomyListingMixin(HtmxListingMixin):
    listing_results_template = "patterns/pages/listing/listing_results--taxonomy.html"

    def get_filter_state(self, request):
        return TaxonomyFilterState.from_request(
            request,
            valid_sector_slugs=set(Sector.objects.values_list("slug", flat=True)),
            valid_service_slugs=set(Service.objects.values_list("slug", flat=True)),
            valid_division_slugs=set(
                DivisionPage.objects.live().public().values_list("slug", flat=True)
            ),
        )

    def get_selection_labels(self, filter_state):
        return {
            "sector": dict(
                Sector.objects.filter(slug__in=filter_state.sectors).values_list(
                    "slug", "name"
                )
            ),
            "service": dict(
                Service.objects.filter(slug__in=filter_state.services).values_list(
                    "slug", "name"
                )
            ),
            "division": dict(
                DivisionPage.objects.filter(
                    slug__in=filter_state.divisions
                ).values_list("slug", "title")
            ),
        }

    def get_used_sectors(self, queryset):
        return Sector.objects.filter(
            pk__in=queryset.values("related_sectors")
        ).order_by("sort_order", "name")

    def get_used_services(self, queryset):
        return Service.objects.filter(
            pk__in=queryset.values("related_services")
        ).order_by("sort_order", "name")

    def get_used_sectors_for_work(self, queryset):
        from django.db import models

        return Sector.objects.filter(
            models.Q(
                pk__in=models.Subquery(queryset.values("workpage__related_sectors"))
            )
            | models.Q(
                pk__in=models.Subquery(
                    queryset.values("historicalworkpage__related_sectors")
                )
            )
        ).order_by("sort_order", "name")

    def get_used_services_for_work(self, queryset):
        from django.db import models

        return Service.objects.filter(
            models.Q(
                pk__in=models.Subquery(queryset.values("workpage__related_services"))
            )
            | models.Q(
                pk__in=models.Subquery(
                    queryset.values("historicalworkpage__related_services")
                )
            )
        ).order_by("sort_order", "name")

    def build_taxonomy_listing_context(
        self,
        request,
        *,
        queryset,
        results_context_key: str,
        page_size: int = 10,
    ):
        filter_state = self.get_filter_state(request)
        selection_labels = self.get_selection_labels(filter_state)
        queryset = apply_taxonomy_filters(queryset, filter_state)

        page_number = request.GET.get("page", 1)
        paginated_results = paginate_queryset(queryset, page_number, page_size)

        listing_filters = build_taxonomy_listing_filters(
            base_queryset=self.get_base_queryset(),
            filter_state=filter_state,
            apply_filters=apply_taxonomy_filters,
            get_used_sectors=self.get_used_sectors,
            get_used_services=self.get_used_services,
            selection_labels=selection_labels,
        )

        return {
            results_context_key: paginated_results,
            **self._listing_context(
                request,
                filter_state=filter_state,
                listing_filters=listing_filters,
                selection_labels=selection_labels,
                paginated_results=paginated_results,
                listing_results_template=self.listing_results_template,
            ),
        }

    def build_work_listing_context(self, request, *, works_queryset):
        filter_state = self.get_filter_state(request)
        selection_labels = self.get_selection_labels(filter_state)
        works_queryset = apply_work_page_filters(works_queryset, filter_state)

        page_number = request.GET.get("page", 1)
        paginated_works = paginate_queryset(works_queryset, page_number, 10)

        listing_filters = build_taxonomy_listing_filters(
            base_queryset=self.works,
            filter_state=filter_state,
            apply_filters=apply_work_page_filters,
            get_used_sectors=self.get_used_sectors_for_work,
            get_used_services=self.get_used_services_for_work,
            selection_labels=selection_labels,
        )

        return {
            "works": paginated_works,
            **self._listing_context(
                request,
                filter_state=filter_state,
                listing_filters=listing_filters,
                selection_labels=selection_labels,
                paginated_results=paginated_works,
                listing_results_template="patterns/pages/listing/listing_results--work.html",
            ),
        }

    def _listing_context(
        self,
        request,
        *,
        filter_state: TaxonomyFilterState,
        listing_filters: TaxonomyListingFilters,
        selection_labels: dict[str, dict[str, str]],
        paginated_results,
        listing_results_template: str,
    ) -> dict:
        listing_path = self.get_url(request)

        selected_filters = build_selected_filter_items(
            listing_path,
            filter_state,
            filter_state.selected_labels(
                sector_labels=listing_filters.sector_labels,
                service_labels=listing_filters.service_labels,
                division_labels=selection_labels.get("division", {}),
            ),
        )

        return {
            "filter_state": filter_state,
            "listing_filters": listing_filters.options,
            "listing_filter_visibility": listing_filters.visibility,
            "listing_result_count": paginated_results.paginator.count,
            "culture_service_slugs": sorted(CULTURE_SERVICE_SLUGS),
            **_selected_service_filters(filter_state),
            **build_listing_urls_context(
                listing_path=listing_path,
                filter_state=filter_state,
                selected_filters=selected_filters,
                page_title=self.title,
            ),
            "listing_htmx_enabled": True,
            "listing_filters_template": "patterns/molecules/listing-filters/listing-filters--taxonomy.html",
            "listing_results_template": listing_results_template,
        }

    def get_base_queryset(self):
        raise NotImplementedError


class BlogIndexPageMixin(TaxonomyListingMixin):
    def get_base_queryset(self):
        return self.blog_posts

    def build_blog_listing_context(self, request):
        return self.build_taxonomy_listing_context(
            request,
            queryset=self.blog_posts,
            results_context_key="blog_posts",
        )
