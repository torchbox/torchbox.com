class PrimaryMobileMenu {
    static selector() {
        return '[data-primary-mobile-menu-toggle]';
    }

    constructor(node) {
        this.node = node;
        this.body = document.querySelector('body');
        this.primaryMobileMenu = document.querySelector(
            '[data-primary-mobile-menu]',
        );
        this.lastMenuItem = document.querySelector(
            '[data-last-menu-item-primary-mobile]',
        );

        this.state = {
            open: false,
        };

        this.bindEventListeners();
    }

    closeSubMenus() {
        this.primaryMobileMenu
            .querySelectorAll('[data-primary-subnav]')
            .forEach((subnav) => {
                subnav.classList.remove('is-visible');
            });
        this.primaryMobileMenu
            .querySelectorAll('[data-open-primary-subnav]')
            .forEach((button) => {
                button.setAttribute('aria-expanded', 'false');
            });
        this.primaryMobileMenu.classList.remove('primary-nav-mobile--subnav-open');
    }

    bindEventListeners() {
        this.node.addEventListener('click', () => {
            if (this.state.open) {
                this.close();
            } else {
                this.open();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && this.state.open) {
                if (
                    this.primaryMobileMenu.querySelector(
                        '[data-primary-subnav].is-visible',
                    )
                ) {
                    this.closeSubMenus();
                    return;
                }
                this.close();
            }
        });

        document.addEventListener('click', (event) => {
            const clickedInsideMenu =
                this.primaryMobileMenu.contains(event.target) ||
                this.node.contains(event.target);

            if (this.state.open && !clickedInsideMenu) {
                this.close();
            }
        });

        document.addEventListener('onMenuOpen', () => {
            if (this.state.open) {
                this.close();
            }
        });

        document.addEventListener('onSearchOpen', () => {
            if (this.state.open) {
                this.close();
            }
        });

        if (this.lastMenuItem) {
            this.lastMenuItem.addEventListener('focusout', () => {
                if (this.state.open) {
                    this.close();
                }
            });
        }
    }

    open() {
        const menuOpenEvent = new Event('onMenuOpen');
        document.dispatchEvent(menuOpenEvent);
        this.node.setAttribute('aria-expanded', 'true');
        this.node.classList.add('is-open');
        this.body.classList.add('no-scroll');
        this.primaryMobileMenu.classList.add('is-visible');
        this.state.open = true;
    }

    close() {
        this.closeSubMenus();
        this.node.setAttribute('aria-expanded', 'false');
        this.node.classList.remove('is-open');
        this.body.classList.remove('no-scroll');
        this.primaryMobileMenu.classList.remove('is-visible');
        this.state.open = false;
    }
}

export default PrimaryMobileMenu;
