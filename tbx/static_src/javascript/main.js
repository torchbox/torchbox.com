import MobileMenu from './components/mobile-menu';
import MobileSubMenu from './components/mobile-sub-menu';
import DesktopSubMenu from './components/desktop-sub-menu';
import DesktopCloseMenus from './components/desktop-close-menus';
import SkipLink from './components/skip-link';
import CookieWarning from './components/cookie-message';
import Tabs from './components/tabs';

// IE11 polyfills
import foreachPolyfill from './polyfills/foreach-polyfill';
import closestPolyfill from './polyfills/closest-polyfill';

import '../sass/main.scss';

foreachPolyfill();
closestPolyfill();

function initComponent(ComponentClass) {
    const items = document.querySelectorAll(ComponentClass.selector());
    items.forEach((item) => new ComponentClass(item));
}

document.addEventListener('DOMContentLoaded', () => {
    /* eslint-disable no-new */
    initComponent(MobileMenu);
    initComponent(MobileSubMenu);
    initComponent(DesktopSubMenu);
    initComponent(SkipLink);
    initComponent(CookieWarning);
    initComponent(Tabs);
    new DesktopCloseMenus();
});
