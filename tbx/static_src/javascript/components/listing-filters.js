const LISTING_PANEL_SELECTOR = '#listing-panel';
const DROPDOWN_PANEL_OPEN_CLASS = 'listing-filters__dropdown-panel--open';

function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function openDropdownPanel(dropdown) {
    const toggle = dropdown.querySelector('[data-listing-filter-toggle]');
    const panel = dropdown.querySelector('[data-listing-filter-panel]');
    if (!toggle || !panel) {
        return;
    }

    toggle.setAttribute('aria-expanded', 'true');
    panel.hidden = false;
    requestAnimationFrame(() => {
        panel.classList.add(DROPDOWN_PANEL_OPEN_CLASS);
    });
}

function closeDropdownPanel(dropdown, { immediate = false } = {}) {
    const toggle = dropdown.querySelector('[data-listing-filter-toggle]');
    const panel = dropdown.querySelector('[data-listing-filter-panel]');
    if (!toggle || !panel || panel.hidden) {
        return;
    }

    toggle.setAttribute('aria-expanded', 'false');
    panel.classList.remove(DROPDOWN_PANEL_OPEN_CLASS);

    if (immediate || prefersReducedMotion()) {
        panel.hidden = true;
        return;
    }

    const finishClose = (event) => {
        if (event.target !== panel || event.propertyName !== 'opacity') {
            return;
        }
        panel.hidden = true;
        panel.removeEventListener('transitionend', finishClose);
        clearTimeout(fallbackTimer);
    };

    panel.addEventListener('transitionend', finishClose);
    const fallbackTimer = setTimeout(() => {
        if (!panel.classList.contains(DROPDOWN_PANEL_OPEN_CLASS) && !panel.hidden) {
            panel.hidden = true;
            panel.removeEventListener('transitionend', finishClose);
        }
    }, 300);
}

function closeDropdown(dropdown, options) {
    closeDropdownPanel(dropdown, options);
}

function closeAllDropdowns(container) {
    container.querySelectorAll('[data-listing-filter-dropdown]').forEach((dropdown) => {
        closeDropdown(dropdown);
    });
}

function updateDropdownCounts(form) {
    form.querySelectorAll('[data-listing-filter-dropdown]').forEach((dropdown) => {
        const count = dropdown.querySelector('[data-listing-filter-count]');
        const checked = dropdown.querySelectorAll('input:checked').length;
        if (!count) {
            return;
        }
        count.textContent = String(checked);
        count.hidden = checked === 0;
    });
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

    const timingInputs = form.querySelectorAll('input[type="radio"][name="timing"]');
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

    form.querySelectorAll('input[type="radio"][name="type"]').forEach((input) => {
        if (!input.name) {
            return;
        }
        input.checked = params.getAll(input.name).includes(input.value);
    });

    updateDropdownCounts(form);
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
        if (form) {
            updateDropdownCounts(form);
        }
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
        updateDropdownCounts(form);
    });

    panel.querySelectorAll('[data-listing-filters-submit]').forEach((button) => {
        button.hidden = true;
    });
}

export {
    LISTING_PANEL_SELECTOR,
    bindListingFilterDelegation,
    initListingFilters,
    syncFilterFormFromUrl,
};
