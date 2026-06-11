// Adds "close" functionality for all desktop sub-menus at once.
// It's a separate class because it captures events outside those components.

import PrimaryDesktopSubMenu from './primary-desktop-sub-menu';

class DesktopCloseMenus {
    constructor() {
        this.primaryDesktopSubMenus = document.querySelectorAll(
            PrimaryDesktopSubMenu.selector(),
        );
        this.allPrimaryNavs = document.querySelectorAll(
            '[data-primary-desktop-menu] .primary-nav-desktop__list',
        );
        this.primaryMobileNav = document.querySelector(
            '[data-primary-mobile-menu]',
        );
        this.body = document.querySelector('body');
        this.bindEvents();
    }

    closeDesktopMenus() {
        this.primaryDesktopSubMenus.forEach((item) => {
            item.closest('[data-has-subnav]').classList.remove('active');
            item.setAttribute('aria-expanded', 'false');
        });

        this.body.classList.remove('no-scroll');
    }

    // Close desktop menus when clicking on document
    closeMenus(e) {
        let close = true;

        this.allPrimaryNavs.forEach((item) => {
            if (item.contains(e.target)) {
                close = false;
            }
        });

        if (
            this.primaryMobileNav &&
            this.primaryMobileNav.classList.contains('is-visible')
        ) {
            close = false;
        }

        if (close) {
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

        document.addEventListener('touchstart', (e) => {
            this.closeMenus(e);
        });

        document.addEventListener('click', (e) => {
            this.closeMenus(e);
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeDesktopMenus();
            }
        });
    }
}

export default DesktopCloseMenus;
