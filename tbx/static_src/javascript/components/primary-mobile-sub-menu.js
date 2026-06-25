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
        this.backLink = this.subnav.querySelector('[data-primary-subnav-back]');
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
