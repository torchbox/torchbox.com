import htmx from 'htmx.org';
import {
    LISTING_PANEL_SELECTOR,
    bindListingFilterDelegation,
    initListingFilters,
} from './components/listing-filters';

window.htmx = htmx;

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

    if (!isPanel && !isResults) {
        return;
    }

    const panel = isPanel ? event.target : event.target.closest('#listing-panel');
    if (!panel) {
        return;
    }

    if (isPanel) {
        htmx.process(event.target);
    }

    initListingFilters(panel);
});
