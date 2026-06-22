import htmx from 'htmx.org';
import {
    LISTING_PANEL_SELECTOR,
    bindListingFilterDelegation,
    bindListingFilterHtmxConfig,
    handleListingFilterSettle,
    initListingFilters,
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
    bindListingFilterHtmxConfig();
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
    const isResults = event.target.classList.contains('listing-panel__results');

    if (!isResults) {
        return;
    }

    if (wasListingPaginationRequest(event)) {
        scrollToListingResults(event.target);
    }
});

document.body.addEventListener('htmx:afterSettle', (event) => {
    handleListingFilterSettle(event);
});
