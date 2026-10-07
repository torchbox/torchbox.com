import { trapFocus } from './focus-trap';

function isMobileMenuFocusTrapTabbable(element) {
    const hiddenSubnav = element.closest('[data-primary-subnav]');

    if (hiddenSubnav && !hiddenSubnav.classList.contains('is-visible')) {
        return false;
    }

    if (element.disabled || element.getAttribute('aria-hidden') === 'true') {
        return false;
    }

    let parent = element.parentElement;
    while (parent) {
        const style = window.getComputedStyle(parent);

        if (
            style.visibility === 'hidden' ||
            style.display === 'none' ||
            parent.getAttribute('aria-hidden') === 'true'
        ) {
            return false;
        }

        parent = parent.parentElement;
    }

    return true;
}

class PrimaryMobileMenu {
    static selector() {
        return '[data-primary-mobile-menu-toggle]';
    }

    static menuSelector() {
        return '[data-primary-mobile-menu]';
    }

    constructor(node) {
        this.node = node;
        this.body = document.querySelector('body');
        this.primaryMobileMenu = document.querySelector(
            PrimaryMobileMenu.menuSelector(),
        );
        this.header = this.node.closest('.header');

        if (!this.primaryMobileMenu) {
            return;
        }

        this.state = {
            open: false,
        };

        this.bindEventListeners();
    }

    getFocusTrapRoots() {
        if (!this.primaryMobileMenu) {
            return [];
        }

        const visibleSubnav = this.primaryMobileMenu.querySelector(
            '[data-primary-subnav].is-visible',
        );

        if (visibleSubnav) {
            return [visibleSubnav];
        }

        return [this.node, this.primaryMobileMenu];
    }

    closeSubMenus({ restoreFocus = false } = {}) {
        if (!this.primaryMobileMenu) {
            return;
        }

        const visibleSubnav = this.primaryMobileMenu.querySelector(
            '[data-primary-subnav].is-visible',
        );
        const triggerToFocus =
            restoreFocus && visibleSubnav
                ? this.primaryMobileMenu.querySelector(
                      `[data-open-primary-subnav][aria-controls="${visibleSubnav.id}"]`,
                  )
                : null;

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
        this.primaryMobileMenu.classList.remove(
            'primary-nav-mobile--subnav-open',
        );

        if (triggerToFocus) {
            triggerToFocus.focus();
        }
    }

    bindEventListeners() {
        this.node.addEventListener('click', () => {
            if (this.state.open) {
                this.close({ restoreFocus: true });
            } else {
                this.open();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (!this.state.open) {
                return;
            }

            if (event.key === 'Escape') {
                if (
                    this.primaryMobileMenu.querySelector(
                        '[data-primary-subnav].is-visible',
                    )
                ) {
                    this.closeSubMenus({ restoreFocus: true });
                    return;
                }
                this.close({ restoreFocus: true });
                return;
            }

            trapFocus(event, this.getFocusTrapRoots(), {
                isTabbable: isMobileMenuFocusTrapTabbable,
            });
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
    }

    open() {
        const menuOpenEvent = new Event('onMenuOpen');
        document.dispatchEvent(menuOpenEvent);
        this.node.setAttribute('aria-expanded', 'true');
        this.node.classList.add('is-open');
        this.body.classList.add('no-scroll');
        this.primaryMobileMenu.classList.add('is-visible');
        if (this.header) {
            this.header.classList.add('header--mobile-menu-open');
        }
        this.state.open = true;
    }

    close({ restoreFocus = false } = {}) {
        this.closeSubMenus();
        this.node.setAttribute('aria-expanded', 'false');
        this.node.classList.remove('is-open');
        this.body.classList.remove('no-scroll');
        this.primaryMobileMenu.classList.remove('is-visible');
        if (this.header) {
            this.header.classList.remove('header--mobile-menu-open');
        }
        this.state.open = false;
        if (restoreFocus) {
            this.node.focus();
        }
    }
}

export default PrimaryMobileMenu;
