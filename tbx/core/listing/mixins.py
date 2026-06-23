from __future__ import annotations

from tbx.core.listing.filters import (
    CULTURE_SERVICE_SLUGS,
    TaxonomyFilterState,
    apply_taxonomy_filters,
    apply_work_page_filters,
    build_listing_urls_context,
    build_selected_filter_items,
    filter_state_for_facet,
    get_listing_paths,
    merge_selected_filter_options,
    paginate_queryset,
    split_service_filter_options,
    split_service_filter_slugs,
)
from tbx.divisions.models import DivisionPage
from tbx.taxonomy.models import Sector, Service


def _format_filter_options(queryset, *, label_attr: str) -> list[dict[str, str]]:
    return [
        {"value": item.slug, "label": getattr(item, label_attr)} for item in queryset
    ]


def _division_labels_for_state(filter_state: TaxonomyFilterState) -> dict[str, str]:
    if not filter_state.divisions:
        return {}
    return dict(
        DivisionPage.objects.filter(slug__in=filter_state.divisions).values_list(
            "slug", "title"
        )
    )


def _sector_labels_for_state(filter_state: TaxonomyFilterState) -> dict[str, str]:
    if not filter_state.sectors:
        return {}
    return dict(
        Sector.objects.filter(slug__in=filter_state.sectors).values_list("slug", "name")
    )


def _service_labels_for_state(filter_state: TaxonomyFilterState) -> dict[str, str]:
    if not filter_state.services:
        return {}
    return dict(
        Service.objects.filter(slug__in=filter_state.services).values_list(
            "slug", "name"
        )
    )


def _taxonomy_listing_filter_visibility(
    *,
    base_queryset,
    filter_state: TaxonomyFilterState,
    listing_filters: dict,
    apply_filters,
    get_used_sectors,
    get_used_services,
) -> dict[str, bool]:
    """Whether each taxonomy dropdown should be shown (baseline options or active selection)."""
    if filter_state.has_filters:
        listing_filters, _, _ = _build_facet_taxonomy_listing_filters(
            base_queryset=base_queryset,
            filter_state=TaxonomyFilterState(),
            apply_filters=apply_filters,
            get_used_sectors=get_used_sectors,
            get_used_services=get_used_services,
        )

    selected_services, selected_culture = split_service_filter_slugs(
        filter_state.services
    )
    return {
        "sector": bool(listing_filters["sectors"]) or bool(filter_state.sectors),
        "service": bool(listing_filters["services"]) or bool(selected_services),
        "culture": bool(listing_filters["culture"]) or bool(selected_culture),
    }


def _build_facet_taxonomy_listing_filters(
    *,
    base_queryset,
    filter_state: TaxonomyFilterState,
    apply_filters,
    get_used_sectors,
    get_used_services,
) -> tuple[dict[str, list[dict[str, str]]], dict[str, str], dict[str, str]]:
    sector_qs = apply_filters(
        base_queryset, filter_state_for_facet(filter_state, "sector")
    )
    service_qs = apply_filters(
        base_queryset, filter_state_for_facet(filter_state, "service")
    )
    culture_qs = apply_filters(
        base_queryset, filter_state_for_facet(filter_state, "culture")
    )

    sectors = get_used_sectors(sector_qs)
    services = get_used_services(service_qs)
    culture_services = get_used_services(culture_qs)

    selected_services, selected_culture = split_service_filter_slugs(
        filter_state.services
    )

    sector_labels = {
        **{sector.slug: sector.name for sector in sectors},
        **_sector_labels_for_state(filter_state),
    }
    service_labels = {
        **{service.slug: service.name for service in services},
        **{service.slug: service.name for service in culture_services},
        **_service_labels_for_state(filter_state),
    }

    listing_filters = {
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
    return listing_filters, sector_labels, service_labels


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

    def is_htmx_request(self, request) -> bool:
        return request.headers.get("HX-Request") == "true"


class TaxonomyListingMixin(HtmxListingMixin):
    listing_results_template = "patterns/pages/listing/listing_results--taxonomy.html"

    def get_taxonomy_filter_slugs(self):
        return {
            "sector": set(Sector.objects.values_list("slug", flat=True)),
            "service": set(Service.objects.values_list("slug", flat=True)),
            "division": set(
                DivisionPage.objects.live().public().values_list("slug", flat=True)
            ),
        }

    def get_filter_state(self, request) -> TaxonomyFilterState:
        slugs = self.get_taxonomy_filter_slugs()
        return TaxonomyFilterState.from_request(
            request,
            valid_sector_slugs=slugs["sector"],
            valid_service_slugs=slugs["service"],
            valid_division_slugs=slugs["division"],
        )

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

    def get_used_divisions(self, queryset):
        division_ids = set(
            queryset.exclude(division__isnull=True).values_list(
                "division_id", flat=True
            )
        )
        post_paths = list(queryset.values_list("path", flat=True))
        for division in DivisionPage.objects.live().public().only("pk", "path"):
            if any(path.startswith(division.path) for path in post_paths):
                division_ids.add(division.pk)
        return DivisionPage.objects.filter(pk__in=division_ids).order_by("title")

    def get_used_divisions_for_pages(self, queryset):
        division_ids = set(
            queryset.filter(workpage__division__isnull=False).values_list(
                "workpage__division_id", flat=True
            )
        ) | set(
            queryset.filter(historicalworkpage__division__isnull=False).values_list(
                "historicalworkpage__division_id", flat=True
            )
        )
        page_paths = list(queryset.values_list("path", flat=True))
        for division in DivisionPage.objects.live().public().only("pk", "path"):
            if any(path.startswith(division.path) for path in page_paths):
                division_ids.add(division.pk)
        return DivisionPage.objects.filter(pk__in=division_ids).order_by("title")

    def _listing_url_context(self, request, filter_state, page_number):
        listing_path, absolute_base_url = get_listing_paths(self, request)
        current_absolute_url = absolute_base_url
        if query := filter_state.urlencode(page=page_number):
            current_absolute_url = f"{absolute_base_url}?{query}"
        return listing_path, absolute_base_url, current_absolute_url

    def build_taxonomy_listing_context(
        self,
        request,
        *,
        queryset,
        results_context_key: str,
        page_size: int = 10,
        apply_filters=None,
    ):
        filter_state = self.get_filter_state(request)
        if apply_filters:
            queryset = apply_filters(queryset, filter_state)
        else:
            queryset = apply_taxonomy_filters(queryset, filter_state)

        page_number = request.GET.get("page", 1)
        paginated_results = paginate_queryset(queryset, page_number, page_size)

        listing_filters, sector_labels, service_labels = (
            _build_facet_taxonomy_listing_filters(
                base_queryset=self.get_base_queryset(),
                filter_state=filter_state,
                apply_filters=apply_filters or apply_taxonomy_filters,
                get_used_sectors=self.get_used_sectors,
                get_used_services=self.get_used_services,
            )
        )
        division_labels = _division_labels_for_state(filter_state)

        listing_path, absolute_base_url, current_absolute_url = (
            self._listing_url_context(request, filter_state, page_number)
        )

        selected_filters = build_selected_filter_items(
            listing_path,
            filter_state,
            filter_state.selected_labels(
                sector_labels=sector_labels,
                service_labels=service_labels,
                division_labels=division_labels,
            ),
        )

        return {
            results_context_key: paginated_results,
            "filter_state": filter_state,
            "listing_filters": listing_filters,
            "listing_filter_visibility": _taxonomy_listing_filter_visibility(
                base_queryset=self.get_base_queryset(),
                filter_state=filter_state,
                listing_filters=listing_filters,
                apply_filters=apply_filters or apply_taxonomy_filters,
                get_used_sectors=self.get_used_sectors,
                get_used_services=self.get_used_services,
            ),
            "culture_service_slugs": sorted(CULTURE_SERVICE_SLUGS),
            **_selected_service_filters(filter_state),
            **build_listing_urls_context(
                listing_path=listing_path,
                filter_state=filter_state,
                selected_filters=selected_filters,
                page_title=self.title,
                absolute_base_url=absolute_base_url,
                current_absolute_url=current_absolute_url,
                has_page_param="page" in request.GET,
            ),
            "listing_htmx_enabled": True,
            "listing_filters_template": "patterns/molecules/listing-filters/listing-filters--taxonomy.html",
            "listing_results_template": self.listing_results_template,
        }

    def build_work_listing_context(self, request, *, works_queryset):
        filter_state = self.get_filter_state(request)
        works_queryset = apply_work_page_filters(works_queryset, filter_state)

        works = [
            {
                "title": work.title,
                "client": work.client,
                "url": work.url,
                "author": work.first_author,
                "date": work.date,
                "read_time": work.read_time,
                "listing_image": work.listing_image,
            }
            for work in works_queryset
        ]

        page_number = request.GET.get("page", 1)
        paginated_works = paginate_queryset(works, page_number, 10)

        listing_filters, sector_labels, service_labels = (
            _build_facet_taxonomy_listing_filters(
                base_queryset=self.works,
                filter_state=filter_state,
                apply_filters=apply_work_page_filters,
                get_used_sectors=self.get_used_sectors_for_work,
                get_used_services=self.get_used_services_for_work,
            )
        )
        division_labels = _division_labels_for_state(filter_state)

        listing_path, absolute_base_url, current_absolute_url = (
            self._listing_url_context(request, filter_state, page_number)
        )

        selected_filters = build_selected_filter_items(
            listing_path,
            filter_state,
            filter_state.selected_labels(
                sector_labels=sector_labels,
                service_labels=service_labels,
                division_labels=division_labels,
            ),
        )

        return {
            "works": paginated_works,
            "filter_state": filter_state,
            "listing_filters": listing_filters,
            "listing_filter_visibility": _taxonomy_listing_filter_visibility(
                base_queryset=self.works,
                filter_state=filter_state,
                listing_filters=listing_filters,
                apply_filters=apply_work_page_filters,
                get_used_sectors=self.get_used_sectors_for_work,
                get_used_services=self.get_used_services_for_work,
            ),
            "culture_service_slugs": sorted(CULTURE_SERVICE_SLUGS),
            **_selected_service_filters(filter_state),
            **build_listing_urls_context(
                listing_path=listing_path,
                filter_state=filter_state,
                selected_filters=selected_filters,
                page_title=self.title,
                absolute_base_url=absolute_base_url,
                current_absolute_url=current_absolute_url,
                has_page_param="page" in request.GET,
            ),
            "listing_htmx_enabled": True,
            "listing_filters_template": "patterns/molecules/listing-filters/listing-filters--taxonomy.html",
            "listing_results_template": "patterns/pages/listing/listing_results--work.html",
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
