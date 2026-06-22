const LISTING_PANEL_SELECTOR = '#listing-panel';

function closeDropdown(dropdown) {
    const toggle = dropdown.querySelector('[data-listing-filter-toggle]');
    const panel = dropdown.querySelector('[data-listing-filter-panel]');
    if (toggle) {
        toggle.setAttribute('aria-expanded', 'false');
    }
    if (panel) {
        panel.hidden = true;
    }
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
                toggle.setAttribute('aria-expanded', 'true');
                const dropdownPanel = dropdown.querySelector('[data-listing-filter-panel]');
                if (dropdownPanel) {
                    dropdownPanel.hidden = false;
                }
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

export { LISTING_PANEL_SELECTOR, bindListingFilterDelegation, initListingFilters };
