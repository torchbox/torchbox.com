// Adds "close" functionality for all DesktopSubMenus at once.
// It's a separate class because it captures events outside those components.

import DesktopSubMenu from './desktop-sub-menu';

class DesktopCloseMenus {
    constructor() {
        this.desktopSubMenus = document.querySelectorAll(
            DesktopSubMenu.selector(),
        );
        this.allPrimaryNavs = document.querySelectorAll(
            '[data-desktop-menu] [data-primary-nav]',
        );
        this.mobileNav = document.querySelector('[data-mobile-menu]');
        this.mobileNavToggle = document.querySelector(
            '[data-mobile-menu-toggle]',
        );
        this.body = document.querySelector('body');
        this.bindEvents();
    }

    // Close desktop menus when clicking on document
    closeMenus(e) {
        let close = true;

        this.allPrimaryNavs.forEach((item) => {
            if (item.contains(e.target)) {
                // don't close the menus if we are clicking anywhere on the primary navigation
                close = false;
            }
        });

        if (
            this.mobileNav.contains(e.target) ||
            this.mobileNavToggle.contains(e.target) ||
            this.mobileNav.classList.contains('is-visible')
        ) {
            // don't close the menus (or allow the page to scroll) if we are opening the mobile menu or clicking on it
            close = false;
        }

        if (close) {
            this.desktopSubMenus.forEach((item) => {
                item.closest('[data-has-subnav]').classList.remove('active');
                item.setAttribute('aria-expanded', 'false');
                this.body.classList.remove('no-scroll');
            });
        }
    }

    bindEvents() {
        if (this.desktopSubMenus && this.desktopSubMenus.length !== 0) {
            document.addEventListener('touchstart', (e) => {
                this.closeMenus(e);
            });

            document.addEventListener('click', (e) => {
                this.closeMenus(e);
            });

            // Close desktop menu with escape key for improved accessibility
            document.addEventListener('keydown', (event) => {
                if (event.key === 'Escape') {
                    this.desktopSubMenus.forEach((item) => {
                        item.closest('[data-has-subnav]').classList.remove(
                            'active',
                        );
                        item.setAttribute('aria-expanded', 'false');
                    });
                }
            });
        }
    }
}

export default DesktopCloseMenus;
