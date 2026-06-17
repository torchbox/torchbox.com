class PrimaryDesktopSubMenu {
    static selector() {
        return '[data-primary-desktop-menu] [data-open-primary-subnav]';
    }

    constructor(node) {
        this.node = node;
        this.body = document.querySelector('body');
        this.toggleNode = this.node.closest('[data-has-subnav]');
        this.allToggleNodes = document.querySelectorAll(
            '[data-primary-desktop-menu] [data-has-subnav]',
        );
        this.activeClass = 'active';
        this.openBodyClass = 'primary-nav-dropdown-open';
        this.backdrop = document.querySelector('.primary-nav-dropdown-backdrop');
        this.bindEventListeners();
    }

    close() {
        this.toggleNode.classList.remove(this.activeClass);
        this.node.setAttribute('aria-expanded', 'false');
        this.body.classList.remove('no-scroll');
        this.body.classList.remove(this.openBodyClass);

        if (this.backdrop) {
            this.backdrop.setAttribute('aria-hidden', 'true');
        }
    }

    open() {
        const menuOpenEvent = new Event('onMenuOpen');
        document.dispatchEvent(menuOpenEvent);
        this.toggleNode.classList.add(this.activeClass);
        this.node.setAttribute('aria-expanded', 'true');
        this.body.classList.add('no-scroll');
        this.body.classList.add(this.openBodyClass);

        if (this.backdrop) {
            this.backdrop.setAttribute('aria-hidden', 'false');
        }
    }

    bindEventListeners() {
        this.node.addEventListener('click', (e) => {
            e.preventDefault();

            this.allToggleNodes.forEach((item) => {
                if (item !== this.toggleNode) {
                    item.classList.remove(this.activeClass);
                    item.querySelector(
                        '[data-open-primary-subnav]',
                    ).setAttribute('aria-expanded', 'false');
                }
            });

            if (this.toggleNode.classList.contains(this.activeClass)) {
                this.close();
            } else {
                this.open();
            }
        });
    }
}

export default PrimaryDesktopSubMenu;
