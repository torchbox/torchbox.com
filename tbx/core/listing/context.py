from django.http import QueryDict


def _urlencode_selected(selected):
    """URL-encode a ``{param: [values]}`` mapping, preserving repeated params."""
    querydict = QueryDict(mutable=True)
    for param, values in selected.items():
        for value in values:
            querydict.appendlist(param, value)
    return querydict.urlencode()


def _build_dropdowns(form, dropdowns):
    result = []
    for param, label in dropdowns:
        selected = form.cleaned_data.get(param, [])
        options = [
            {
                "value": value,
                "label": choice_label,
                "checked": value in selected,
                "id": f"filter-{param}-{value}",
            }
            for value, choice_label in form.fields[param].choices
        ]
        result.append(
            {
                "param": param,
                "label": label,
                "options": options,
                "selected_count": len(selected),
            }
        )
    return result


def _build_active_filters(base_url, form, dropdowns):
    selected = {param: form.cleaned_data.get(param, []) for param, _ in dropdowns}
    pills = []
    for param, _ in dropdowns:
        value_labels = dict(form.fields[param].choices)
        for value in selected[param]:
            # Each pill's link is the current selection with just this value
            # removed, so following it de-selects that one filter.
            remaining = {p: list(values) for p, values in selected.items()}
            remaining[param] = [v for v in remaining[param] if v != value]
            query = _urlencode_selected(remaining)
            pills.append(
                {
                    "label": value_labels.get(value, value),
                    "remove_url": f"{base_url}?{query}" if query else base_url,
                }
            )
    return pills


def _build_canonical_query_string(request, selected):
    """Return the canonical query string for a listing request."""

    # If paginating content, then just return the current page number,
    # as site crawlers don't need to index filter & page combinations.
    if "page" in request.GET:
        return _urlencode_selected({"page": [request.GET["page"]]})

    # With multiple or no filters applied, return the listing URL without params.
    # With a single filter applied, return the canonical query string for that filter.
    distinct_filters = {
        param: list(dict.fromkeys(values)) for param, values in selected.items()
    }
    filter_count = sum(len(values) for values in distinct_filters.values())
    canonical_params = distinct_filters if filter_count == 1 else {}
    return _urlencode_selected(canonical_params)


def build_listing_filter_context(request, form, dropdowns):
    """Build the template context for the shared listing-filter UI.

    ``dropdowns`` is an iterable of ``(param, label)`` in display order. The
    form must already be validated (``is_valid()`` called). Returns the dropdown
    definitions, active-filter pills, a clear-all URL, and the encoded params
    used by pagination links and the page's canonical URL.
    """
    base_url = request.path
    selected = {param: form.cleaned_data.get(param, []) for param, _ in dropdowns}
    return {
        "filter_dropdowns": _build_dropdowns(form, dropdowns),
        "active_filters": _build_active_filters(base_url, form, dropdowns),
        "clear_filters_url": base_url,
        "extra_url_params": _urlencode_selected(selected),
        "canonical_query_string": _build_canonical_query_string(request, selected),
        "has_active_filters": any(selected.values()),
    }
