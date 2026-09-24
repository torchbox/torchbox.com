import htmx from 'htmx.org';
import PrimaryMobileMenu from './components/primary-mobile-menu';
import PrimaryMobileSubMenu from './components/primary-mobile-sub-menu';
import PrimaryDesktopSubMenu from './components/primary-desktop-sub-menu';
import DesktopCloseMenus from './components/desktop-close-menus';
import SkipLink from './components/skip-link';
import CookieWarning from './components/cookie-message';
import YouTubeConsentManager from './components/youtube-embed';
import Tabs from './components/tabs';
import TableHint from './components/table-hint';
import Modal from './components/modal';
import ModeSwitcher from './components/mode-switcher';
import ListingFilters from './components/listing-filters';

// IE11 polyfills
import foreachPolyfill from './polyfills/foreach-polyfill';
import closestPolyfill from './polyfills/closest-polyfill';

import '../css/tailwind.css';
import '../sass/main.scss';

// Third party imports
import 'lite-youtube-embed/src/lite-yt-embed';

// Components are only initialised on DOMContentLoaded, so restoring HTMX's
// history snapshot would leave them unbound. Do a full page load on back and
// forward instead.
htmx.config.historyCacheSize = 0;
htmx.config.refreshOnHistoryMiss = true;
// Keep HTMX working under a strict CSP.
htmx.config.includeIndicatorStyles = false;
htmx.config.allowEval = false;

foreachPolyfill();
closestPolyfill();

function initComponent(ComponentClass) {
    const items = document.querySelectorAll(ComponentClass.selector());
    items.forEach((item) => new ComponentClass(item));
}

document.addEventListener('DOMContentLoaded', () => {
    /* eslint-disable no-new */
    initComponent(PrimaryMobileMenu);
    initComponent(PrimaryMobileSubMenu);
    initComponent(PrimaryDesktopSubMenu);
    initComponent(SkipLink);
    initComponent(CookieWarning);
    initComponent(YouTubeConsentManager);
    initComponent(Tabs);
    initComponent(TableHint);
    initComponent(Modal);
    initComponent(ModeSwitcher);
    initComponent(ListingFilters);
    new DesktopCloseMenus();

    // Move sticky CTA(s) to the end of the main content for natural tab order
    const main = document.getElementById('main-content') || document.body;
    if (main) {
        document.querySelectorAll('[data-sticky-cta]').forEach((element) => {
            main.appendChild(element);
        });
    }
});
