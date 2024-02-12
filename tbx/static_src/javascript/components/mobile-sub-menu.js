// Expected markup - see primary_nav.html
/* <ul class="primary-nav" data-primary-nav="">
    <li class="primary-nav__item primary-nav__item--is-parent" data-has-subnav="">
        <a class="primary-nav__link" data-open-subnav="" href="/" aria-haspopup="true" aria-expanded="false">
            Home
            <span class="primary-nav__icon">›</span>
        </a>
        <ul class="sub-nav" data-subnav="">
            <li class="sub-nav__item sub-nav__item--back"><a data-subnav-back="" href="#">‹ Back</a></li>
            <li class="sub-nav__item">
                <a class="sub-nav__link" href="/">About us overview</a>
            </li>
            <li class="sub-nav__item sub-nav__item--secondary">
                <a class="sub-nav__link" href="/page-1/">page 1</a>
            </li>
        </ul>
    </li>
</ul> */

class MobileSubMenu {
    static selector() {
        return '[data-mobile-menu] [data-open-subnav]';
    }

    constructor(node) {
        this.node = node;
        this.subnav = this.node.nextElementSibling;
        this.isSubnavChild = this.subnav.hasAttribute('data-subnav-child');
        this.backLink = this.subnav.querySelector('[data-subnav-back]');
        this.bindEventListeners();
    }

    bindEventListeners() {
        // Open submenu
        this.node.addEventListener('click', (e) => {
            e.preventDefault();
            this.open();
        });
        // Click back button to close it
        this.backLink.addEventListener('click', (e) => {
            e.preventDefault();
            this.close();
        });

        // After the end of the sub-nav, the focus moves back to the parent,
        // So close the current sub-navigation
        document.addEventListener('focusin', (e) => {
            const inSubMenu = !!e.target.closest('[data-subnav]');
            const inSubChildMenu = !!e.target.closest('[data-subnav-child]');

            // leaving subnav for primary nav
            if (!inSubMenu) {
                this.subnav.classList.remove('is-visible');
                this.node.setAttribute('aria-expanded', 'false');
            }

            // leaving child subnav for parent subnav
            if (this.isSubnavChild && !inSubChildMenu) {
                this.close();
            }
        });
    }

    open() {
        this.subnav.classList.add('is-visible');
        this.node.setAttribute('aria-expanded', 'true');
    }

    close() {
        this.subnav.classList.remove('is-visible');
        this.node.setAttribute('aria-expanded', 'false');
    }
}

export default MobileSubMenu;
