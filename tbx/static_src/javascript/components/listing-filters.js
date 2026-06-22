const LISTING_PANEL_SELECTOR = '#listing-panel';
const DROPDOWN_PANEL_OPEN_CLASS = 'listing-filters__dropdown-panel--open';
const LISTING_FILTER_DEBOUNCE_MS = 200;

let listingFilterTimer = null;
let pendingOpenDropdownId = null;

function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function getOpenDropdownId(panel) {
    const openPanel = panel?.querySelector(
        '[data-listing-filter-panel].listing-filters__dropdown-panel--open',
    );
    return openPanel?.closest('[data-listing-filter-dropdown]')?.id ?? null;
}

function openDropdownPanel(dropdown) {
    const toggle = dropdown.querySelector('[data-listing-filter-toggle]');
    const panel = dropdown.querySelector('[data-listing-filter-panel]');
    if (!toggle || !panel) {
        return;
    }

    toggle.setAttribute('aria-expanded', 'true');
    panel.setAttribute('aria-hidden', 'false');
    requestAnimationFrame(() => {
        panel.classList.add(DROPDOWN_PANEL_OPEN_CLASS);
    });
}

function closeDropdownPanel(dropdown, { immediate = false } = {}) {
    const toggle = dropdown.querySelector('[data-listing-filter-toggle]');
    const panel = dropdown.querySelector('[data-listing-filter-panel]');
    if (
        !toggle ||
        !panel ||
        !panel.classList.contains(DROPDOWN_PANEL_OPEN_CLASS)
    ) {
        return;
    }

    toggle.setAttribute('aria-expanded', 'false');
    panel.setAttribute('aria-hidden', 'true');
    panel.classList.remove(DROPDOWN_PANEL_OPEN_CLASS);

    if (immediate || prefersReducedMotion()) {
        return;
    }

    const finishClose = (event) => {
        if (event.target !== panel || event.propertyName !== 'opacity') {
            return;
        }
        panel.removeEventListener('transitionend', finishClose);
        clearTimeout(fallbackTimer);
    };

    panel.addEventListener('transitionend', finishClose);
    const fallbackTimer = setTimeout(() => {
        panel.removeEventListener('transitionend', finishClose);
    }, 300);
}

function closeDropdown(dropdown, options) {
    closeDropdownPanel(dropdown, options);
}

function closeAllDropdowns(container) {
    container
        .querySelectorAll('[data-listing-filter-dropdown]')
        .forEach((dropdown) => {
            closeDropdown(dropdown);
        });
}

function restoreOpenDropdown(panel) {
    if (!pendingOpenDropdownId || !panel) {
        return;
    }

    const dropdown = panel.querySelector(`#${pendingOpenDropdownId}`);
    pendingOpenDropdownId = null;
    if (dropdown) {
        openDropdownPanel(dropdown);
    }
}

function getCultureServiceSlugs(form) {
    const value = form?.dataset.listingCultureServiceSlugs;
    if (!value) {
        return new Set();
    }
    return new Set(value.split(',').filter(Boolean));
}

function countFromUrl(dropdownId, params, cultureSlugs) {
    if (dropdownId === 'listing-filter-dropdown-sector') {
        return params.getAll('sector').length;
    }

    if (dropdownId === 'listing-filter-dropdown-service') {
        return params
            .getAll('service')
            .filter((slug) => !cultureSlugs.has(slug)).length;
    }

    if (dropdownId === 'listing-filter-dropdown-culture') {
        return params
            .getAll('service')
            .filter((slug) => cultureSlugs.has(slug)).length;
    }

    if (dropdownId === 'listing-filter-dropdown-type') {
        return params.getAll('type').length;
    }

    return 0;
}

function parametersToSearchParams(parameters) {
    const params = new URLSearchParams();
    Object.entries(parameters).forEach(([key, values]) => {
        const normalised = Array.isArray(values) ? values : [values];
        normalised.forEach((value) => {
            if (value) {
                params.append(key, value);
            }
        });
    });
    return params;
}

function dropdownHasFilterInputs(dropdown) {
    return Boolean(
        dropdown.querySelector(
            '.listing-filters__options input[type="checkbox"], .listing-filters__options input[type="radio"]',
        ),
    );
}

function updateDropdownCounts(form, { parameters = null } = {}) {
    const cultureSlugs = getCultureServiceSlugs(form);
    const params = parameters
        ? parametersToSearchParams(parameters)
        : new URLSearchParams(window.location.search);

    form.querySelectorAll('[data-listing-filter-dropdown]').forEach(
        (dropdown) => {
            const count = dropdown.querySelector('[data-listing-filter-count]');
            if (!count) {
                return;
            }
            const checked = countFromUrl(dropdown.id, params, cultureSlugs);
            count.textContent = String(checked);
            count.hidden = checked === 0;
        },
    );
}

function updateDropdownVisibility(form) {
    if (!form) {
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const cultureSlugs = getCultureServiceSlugs(form);

    form.querySelectorAll('[data-listing-filter-dropdown]').forEach(
        (dropdown) => {
            const hasInputs = dropdownHasFilterInputs(dropdown);
            const selectedCount = countFromUrl(
                dropdown.id,
                params,
                cultureSlugs,
            );
            dropdown.hidden = !hasInputs && selectedCount === 0;
            if (dropdown.hidden) {
                closeDropdown(dropdown, { immediate: true });
            }
        },
    );
}

function collectListingFilterParameters(form) {
    const parameters = {};

    form.querySelectorAll('input[type="checkbox"]:checked').forEach((input) => {
        if (!input.name) {
            return;
        }
        if (!parameters[input.name]) {
            parameters[input.name] = [];
        }
        parameters[input.name].push(input.value);
    });

    const checkedTiming = form.querySelector(
        'input[type="radio"][name="timing"]:checked',
    );
    if (checkedTiming?.name && checkedTiming.value) {
        parameters[checkedTiming.name] = [checkedTiming.value];
    }

    form.querySelectorAll('input[type="radio"][name="type"]:checked').forEach(
        (input) => {
            if (!input.name) {
                return;
            }
            if (!parameters[input.name]) {
                parameters[input.name] = [];
            }
            parameters[input.name].push(input.value);
        },
    );

    return parameters;
}

function refreshListingFilterChrome(
    form,
    { parameters = null, skipVisibility = false } = {},
) {
    if (!form) {
        return;
    }
    updateDropdownCounts(form, { parameters });
    if (!skipVisibility) {
        updateDropdownVisibility(form);
    }
}

function syncFilterFormFromUrl(form) {
    if (!form) {
        return;
    }

    const params = new URLSearchParams(window.location.search);

    form.querySelectorAll('input[type="checkbox"]').forEach((input) => {
        if (!input.name) {
            return;
        }
        input.checked = params.getAll(input.name).includes(input.value);
    });

    const timingInputs = form.querySelectorAll(
        'input[type="radio"][name="timing"]',
    );
    if (timingInputs.length) {
        const timing = params.get('timing');
        timingInputs.forEach((input) => {
            if (timing) {
                input.checked = input.value === timing;
            } else {
                input.checked = input.value === 'upcoming';
            }
        });
    }

    form.querySelectorAll('input[type="radio"][name="type"]').forEach(
        (input) => {
            if (!input.name) {
                return;
            }
            input.checked = params.getAll(input.name).includes(input.value);
        },
    );

    refreshListingFilterChrome(form);
}

function submitListingFilters(form) {
    const panel = form.closest(LISTING_PANEL_SELECTOR);
    if (!panel || typeof window.htmx === 'undefined') {
        return;
    }

    pendingOpenDropdownId = getOpenDropdownId(panel);
    const url = form.dataset.listingFiltersUrl || form.getAttribute('action');
    const parameters = collectListingFilterParameters(form);

    window.htmx.ajax('GET', url, {
        source: form,
        target: '.listing-panel__results',
        select: '.listing-panel__results',
        swap: 'innerHTML',
        values: parameters,
        push: 'true',
        headers: { 'HX-Request': 'true' },
    });
}

function scheduleListingFilterRequest(form) {
    clearTimeout(listingFilterTimer);
    listingFilterTimer = setTimeout(() => {
        submitListingFilters(form);
    }, LISTING_FILTER_DEBOUNCE_MS);
}

function bindListingFilterHtmxConfig() {
    if (document.body.dataset.listingFiltersHtmxBound === 'true') {
        return;
    }
    document.body.dataset.listingFiltersHtmxBound = 'true';

    window.addEventListener('popstate', () => {
        const panel = document.querySelector(LISTING_PANEL_SELECTOR);
        const form = panel?.querySelector('[data-listing-filters]');
        syncFilterFormFromUrl(form);
    });
}

function bindListingFilterDelegation() {
    if (document.body.dataset.listingFiltersBound === 'true') {
        return;
    }
    document.body.dataset.listingFiltersBound = 'true';

    document.addEventListener('change', (event) => {
        const input = event.target;
        if (!input.matches('[data-listing-filters] input')) {
            return;
        }
        const form = input.closest('[data-listing-filters]');
        if (!form) {
            return;
        }
        refreshListingFilterChrome(form, {
            parameters: collectListingFilterParameters(form),
            skipVisibility: true,
        });
        scheduleListingFilterRequest(form);
    });

    document.addEventListener('click', (event) => {
        const panel = document.querySelector(LISTING_PANEL_SELECTOR);
        if (!panel) {
            return;
        }

        const toggle = event.target.closest('[data-listing-filter-toggle]');
        if (toggle) {
            event.preventDefault();
            const dropdown = toggle.closest('[data-listing-filter-dropdown]');
            if (!dropdown) {
                return;
            }
            const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
            closeAllDropdowns(panel);
            if (!isExpanded) {
                openDropdownPanel(dropdown);
            }
            return;
        }

        if (!event.target.closest('[data-listing-filter-dropdown]')) {
            closeAllDropdowns(panel);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') {
            return;
        }
        const panel = document.querySelector(LISTING_PANEL_SELECTOR);
        if (!panel) {
            return;
        }
        closeAllDropdowns(panel);
    });
}

function initListingFilters(panel) {
    panel.querySelectorAll('[data-listing-filters]').forEach((form) => {
        if (form.dataset.listingFiltersInitialised === 'true') {
            return;
        }
        form.dataset.listingFiltersInitialised = 'true';

        form.querySelectorAll('[data-listing-filter-panel]').forEach(
            (filterPanel) => {
                filterPanel.setAttribute('aria-hidden', 'true');
            },
        );

        form.querySelectorAll('[data-listing-filters-submit]').forEach(
            (button) => {
                button.hidden = true;
            },
        );

        syncFilterFormFromUrl(form);
    });
}

function isListingPanelHtmxEvent(event) {
    const requestElement = event.detail.requestConfig?.elt;
    if (requestElement?.closest?.('#listing-panel')) {
        return true;
    }

    const target = event.detail.target;
    if (!(target instanceof Element)) {
        return false;
    }

    return (
        Boolean(target.closest('#listing-panel'))
        || target.classList.contains('listing-panel__results')
        || target.id === 'listing-active-filters'
        || target.classList.contains('listing-filters__options')
    );
}

function handleListingFilterSettle(event) {
    if (!isListingPanelHtmxEvent(event)) {
        return;
    }

    const panel = document.querySelector(LISTING_PANEL_SELECTOR);
    if (!panel) {
        return;
    }

    const form = panel.querySelector('[data-listing-filters]');
    const results = panel.querySelector('.listing-panel__results');
    const requestElement = event.detail.requestConfig?.elt;

    if (results) {
        window.htmx.process(results);
    }

    syncFilterFormFromUrl(form);

    if (requestElement?.matches?.('[data-listing-filters]')) {
        restoreOpenDropdown(panel);
    } else {
        pendingOpenDropdownId = null;
    }
}

function handleListingFilterSwap(event) {
    if (!isListingPanelHtmxEvent(event)) {
        return;
    }

    const target = event.detail.target;
    if (!(target instanceof Element)) {
        return;
    }

    const shouldSyncForm =
        target.id === 'listing-active-filters'
        || target.classList.contains('listing-filters__options');

    if (!shouldSyncForm) {
        return;
    }

    const panel = document.querySelector(LISTING_PANEL_SELECTOR);
    const form = panel?.querySelector('[data-listing-filters]');
    syncFilterFormFromUrl(form);
}

export {
    LISTING_PANEL_SELECTOR,
    bindListingFilterDelegation,
    bindListingFilterHtmxConfig,
    handleListingFilterSettle,
    handleListingFilterSwap,
    initListingFilters,
    refreshListingFilterChrome,
    restoreOpenDropdown,
    syncFilterFormFromUrl,
};
