import { trapFocus } from './focus-trap';

class PrimaryMobileSubMenu {
    static selector() {
        return '[data-primary-mobile-menu] [data-open-primary-subnav]';
    }

    constructor(node) {
        this.node = node;
        this.mobileMenu = this.node.closest('[data-primary-mobile-menu]');
        this.subnav = document.getElementById(
            this.node.getAttribute('aria-controls'),
        );
        this.backLink = this.subnav?.querySelector(
            '[data-primary-subnav-back]',
        );

        if (!this.subnav || !this.backLink || !this.mobileMenu) {
            return;
        }

        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('click', (e) => {
            e.preventDefault();
            this.open();
        });

        this.backLink.addEventListener('click', (e) => {
            e.preventDefault();
            this.close();
        });

        // Trap the focus inside the submenu while it's open
        document.addEventListener('keydown', (event) => {
            if (!this.subnav.classList.contains('is-visible')) {
                return;
            }

            trapFocus(event, [this.subnav]);
        });
    }

    open() {
        this.subnav.classList.add('is-visible');
        this.node.setAttribute('aria-expanded', 'true');
        this.mobileMenu.classList.add('primary-nav-mobile--subnav-open');
        this.backLink.focus();
    }

    close() {
        this.subnav.classList.remove('is-visible');
        this.node.setAttribute('aria-expanded', 'false');
        this.mobileMenu.classList.remove('primary-nav-mobile--subnav-open');
        this.node.focus();
    }
}

export default PrimaryMobileSubMenu;
