import htmx from 'htmx.org';
import {
    LISTING_PANEL_SELECTOR,
    bindListingFilterDelegation,
    initListingFilters,
    syncFilterFormFromUrl,
} from './components/listing-filters';

window.htmx = htmx;

function scrollToListingResults(resultsElement) {
    if (!resultsElement) {
        return;
    }

    const behavior = window.matchMedia('(prefers-reduced-motion: reduce)')
        .matches
        ? 'auto'
        : 'smooth';
    resultsElement.scrollIntoView({ behavior, block: 'start' });
}

function wasListingPaginationRequest(event) {
    return Boolean(
        event.detail.requestConfig?.elt?.closest('[data-listing-pagination]'),
    );
}

function initListingPage() {
    bindListingFilterDelegation();
    htmx.process(document.body);

    const panel = document.querySelector(LISTING_PANEL_SELECTOR);
    if (panel) {
        initListingFilters(panel);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initListingPage);
} else {
    initListingPage();
}

document.body.addEventListener('htmx:afterSwap', (event) => {
    const isPanel = event.target.id === 'listing-panel';
    const isResults = event.target.classList.contains('listing-panel__results');
    const isActiveFilters = event.target.id === 'listing-active-filters';

    if (!isPanel && !isResults && !isActiveFilters) {
        return;
    }

    const panel = isPanel
        ? event.target
        : event.target.closest('#listing-panel');
    if (!panel) {
        return;
    }

    if (isPanel) {
        htmx.process(event.target);
    }

    const form = panel.querySelector('[data-listing-filters]');
    if (isResults || isActiveFilters) {
        syncFilterFormFromUrl(form);
    }

    if (isResults && wasListingPaginationRequest(event)) {
        scrollToListingResults(event.target);
    }

    initListingFilters(panel);
});
