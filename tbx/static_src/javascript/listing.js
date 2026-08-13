import htmx from 'htmx.org';
import {
    LISTING_PANEL_SELECTOR,
    bindListingFilterDelegation,
    bindListingFilterHtmxConfig,
    handleListingFilterSettle,
    handleListingFilterSwap,
    initListingFilters,
} from './components/listing-filters';

window.htmx = htmx;

// Don't let htmx snapshot and restore whole pages for back/forward navigation.
//
// Restoring a snapshot re-runs the page's scripts, and main.js registers custom
// elements at import time — so going back after a filter change threw
// `NotSupportedError: the name "lite-youtube" has already been used`. A real
// navigation costs a round trip but renders the filtered state from the URL
// server-side, which is what we want anyway.
htmx.config.historyCacheSize = 0;
htmx.config.refreshOnHistoryMiss = true;

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

document.body.addEventListener('htmx:afterSwap', (event) => {
    handleListingFilterSwap(event);
});

document.body.addEventListener('htmx:afterSettle', (event) => {
    handleListingFilterSettle(event);
});
