const LISTING_PANEL_SELECTOR = '#listing-panel';
const LISTING_RESULTS_SELECTOR = '[data-listing-results]';
const FOCUSABLE_SELECTOR = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
].join(',');
let pendingOpenDropdownId = null;

function getOpenDropdownId(panel) {
    return panel
        ?.querySelector('[data-listing-filter-toggle][aria-expanded="true"]')
        ?.closest('[data-listing-filter-dropdown]')?.id;
}

function openDropdown(dropdown) {
    dropdown
        .querySelector('[data-listing-filter-toggle]')
        ?.setAttribute('aria-expanded', 'true');
    const panel = dropdown.querySelector('[data-listing-filter-panel]');
    if (panel) panel.hidden = false;
}

function closeDropdown(dropdown) {
    dropdown
        .querySelector('[data-listing-filter-toggle]')
        ?.setAttribute('aria-expanded', 'false');
    const panel = dropdown.querySelector('[data-listing-filter-panel]');
    if (panel) panel.hidden = true;
}

function closeAllDropdowns(container, { except = null } = {}) {
    container
        .querySelectorAll('[data-listing-filter-dropdown]')
        .forEach((dropdown) => {
            if (dropdown !== except) {
                closeDropdown(dropdown);
            }
        });
}

function restoreOpenDropdown(panel) {
    if (!pendingOpenDropdownId || !panel) {
        return;
    }

    const dropdown = panel.querySelector(`#${pendingOpenDropdownId}`);
    pendingOpenDropdownId = null;
    if (dropdown) {
        openDropdown(dropdown);
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
        return params.getAll('service').filter((slug) => cultureSlugs.has(slug))
            .length;
    }

    if (dropdownId === 'listing-filter-dropdown-timing') {
        return params.getAll('timing').length;
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

    return parameters;
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

    updateDropdownCounts(form);
}

function announceListingUpdate(panel) {
    const announcer = panel.querySelector('[data-listing-announcer]');
    if (!announcer) {
        return;
    }

    const results = panel.querySelector('[data-listing-result-count]');
    const count = Number(results?.dataset.listingResultCount);

    if (!Number.isFinite(count)) {
        announcer.textContent = 'Listing updated';
        return;
    }

    if (count === 0) {
        announcer.textContent = 'Listing updated, no results';
        return;
    }

    announcer.textContent = `Listing updated, ${count} ${
        count === 1 ? 'result' : 'results'
    }`;
}

function submitListingFilters(form) {
    const panel = form.closest(LISTING_PANEL_SELECTOR);
    if (!panel || typeof window.htmx === 'undefined') {
        return;
    }

    pendingOpenDropdownId = getOpenDropdownId(panel);
    const url = form.dataset.listingFiltersUrl || form.getAttribute('action');

    window.htmx.ajax('GET', url, {
        source: form,
        target: LISTING_RESULTS_SELECTOR,
        select: LISTING_RESULTS_SELECTOR,
        swap: 'outerHTML',
        values: collectListingFilterParameters(form),
        push: 'true',
        headers: { 'HX-Request': 'true' },
    });
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
        if (!input.matches('[data-listing-filters] input[type="checkbox"]')) {
            return;
        }
        const form = input.closest('[data-listing-filters]');
        if (form) {
            submitListingFilters(form);
        }
    });

    document.addEventListener('click', (event) => {
        const panel = document.querySelector(LISTING_PANEL_SELECTOR);
        if (!panel) {
            return;
        }

        const toggle = event.target.closest('[data-listing-filter-toggle]');
        if (toggle) {
            const dropdown = toggle.closest('[data-listing-filter-dropdown]');
            const willOpen = toggle.getAttribute('aria-expanded') !== 'true';
            closeAllDropdowns(panel);
            if (willOpen) openDropdown(dropdown);
            return;
        }

        if (!event.target.closest('[data-listing-filter-dropdown]')) {
            closeAllDropdowns(panel);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (
            event.key === 'Enter' &&
            event.target.matches?.(
                '[data-listing-filters] input[type="checkbox"]',
            )
        ) {
            // Checkbox activation follows the native/APG convention: Space toggles.
            // Suppress Enter so it cannot submit the surrounding form and close the
            // disclosure, but do not invent a second activation key.
            event.preventDefault();
            return;
        }

        if (event.key === 'Tab') {
            const dropdown = event.target.closest?.(
                '[data-listing-filter-dropdown]',
            );
            const filterPanel = event.target.closest?.(
                '[data-listing-filter-panel]',
            );
            if (!dropdown || !filterPanel) {
                return;
            }

            const panelControls = Array.from(
                filterPanel.querySelectorAll(FOCUSABLE_SELECTOR),
            );
            const firstControl = panelControls[0];
            const lastControl = panelControls[panelControls.length - 1];

            if (event.shiftKey && event.target === firstControl) {
                event.preventDefault();
                closeDropdown(dropdown);
                dropdown.querySelector('[data-listing-filter-toggle]')?.focus();
                return;
            }

            if (!event.shiftKey && event.target === lastControl) {
                event.preventDefault();
                closeDropdown(dropdown);
                dropdown.querySelector('[data-listing-filter-toggle]')?.focus();
                return;
            }
        }

        if (event.key !== 'Escape') {
            return;
        }
        const panel = document.querySelector(LISTING_PANEL_SELECTOR);
        if (!panel) {
            return;
        }

        // Closing the dropdown removes whatever had focus from view, which would
        // otherwise drop focus to <body> and leave keyboard users with no visible
        // position. Hand it back to the summary they came from.
        const focusedDropdown = document.activeElement?.closest?.(
            '[data-listing-filter-dropdown]',
        );
        closeAllDropdowns(panel);
        focusedDropdown?.querySelector('[data-listing-filter-toggle]')?.focus();
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
                filterPanel.classList.add(
                    'listing-filters__dropdown-panel--enhanced',
                );
                filterPanel.hidden = true;
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
    if (requestElement?.closest?.(LISTING_PANEL_SELECTOR)) {
        return true;
    }

    const { target } = event.detail;
    if (!(target instanceof Element)) {
        return false;
    }

    return (
        Boolean(target.closest(LISTING_PANEL_SELECTOR)) ||
        target.matches('[data-listing-results]') ||
        target.id === 'listing-active-filters'
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
    const results = panel.querySelector(LISTING_RESULTS_SELECTOR);
    const requestElement = event.detail.requestConfig?.elt;

    if (results) {
        window.htmx.process(results);
    }

    syncFilterFormFromUrl(form);
    announceListingUpdate(panel);

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

    const { target } = event.detail;
    if (!(target instanceof Element)) {
        return;
    }

    if (target.id !== 'listing-active-filters') {
        return;
    }

    const panel = document.querySelector(LISTING_PANEL_SELECTOR);
    const form = panel?.querySelector('[data-listing-filters]');
    syncFilterFormFromUrl(form);
}

export {
    LISTING_PANEL_SELECTOR,
    LISTING_RESULTS_SELECTOR,
    bindListingFilterDelegation,
    bindListingFilterHtmxConfig,
    handleListingFilterSettle,
    handleListingFilterSwap,
    initListingFilters,
    restoreOpenDropdown,
    submitListingFilters,
    syncFilterFormFromUrl,
};
