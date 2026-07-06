// Adds "close" functionality for all desktop sub-menus at once.
// It's a separate class because it captures events outside those components.

import PrimaryDesktopSubMenu from './primary-desktop-sub-menu';
import PrimaryMobileMenu from './primary-mobile-menu';

class DesktopCloseMenus {
    constructor() {
        this.primaryDesktopSubMenus = document.querySelectorAll(
            PrimaryDesktopSubMenu.selector(),
        );
        this.allPrimaryNavs = document.querySelectorAll(
            '[data-primary-desktop-menu] .primary-nav-desktop__list',
        );
        this.primaryMobileNav = document.querySelector(
            PrimaryMobileMenu.menuSelector(),
        );
        this.body = document.querySelector('body');
        this.openBodyClass = 'primary-nav-dropdown-open';
        this.backdrop = document.querySelector(
            '[data-primary-nav-dropdown-backdrop]',
        );
        this.bindEvents();
    }

    closeDesktopMenus() {
        this.primaryDesktopSubMenus.forEach((item) => {
            item.closest('[data-has-subnav]').classList.remove('active');
            item.setAttribute('aria-expanded', 'false');
        });

        this.body.classList.remove('no-scroll');
        this.body.classList.remove(this.openBodyClass);

        if (this.backdrop) {
            this.backdrop.setAttribute('aria-hidden', 'true');
        }
    }

    isOutsideNav(target) {
        if (!target) {
            return true;
        }

        let outside = true;

        this.allPrimaryNavs.forEach((item) => {
            if (item.contains(target)) {
                outside = false;
            }
        });

        if (
            this.primaryMobileNav &&
            this.primaryMobileNav.classList.contains('is-visible')
        ) {
            outside = false;
        }

        return outside;
    }

    // Close desktop menus when clicking on document
    closeMenus(e) {
        if (this.isOutsideNav(e.target)) {
            this.closeDesktopMenus();
        }
    }

    // Close desktop menus when focus (eg. via Tab) moves outside them
    closeMenusOnFocusOut(e) {
        if (this.isOutsideNav(e.relatedTarget)) {
            this.closeDesktopMenus();
        }
    }

    bindEvents() {
        if (
            !this.primaryDesktopSubMenus ||
            this.primaryDesktopSubMenus.length === 0
        ) {
            return;
        }

        document.addEventListener('click', (e) => {
            this.closeMenus(e);
        });

        document.addEventListener('focusout', (e) => {
            this.closeMenusOnFocusOut(e);
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeDesktopMenus();
            }
        });
    }
}

export default DesktopCloseMenus;
