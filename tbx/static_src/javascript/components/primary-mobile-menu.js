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

    bindEventListeners() {
        this.node.addEventListener('click', () => {
            this.open();
        });

        // Close mobile dropdown with escape key for improved accessibility
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                if (this.state.open) {
                    this.close();
                    this.state.open = false;
                }
            }
        });

        // Close mobile dropdown when clicking outside of the menu
        document.addEventListener('click', (event) => {
            if (this.state.open && !this.node.contains(event.target)) {
                this.close();
                this.state.open = false;
            }
        });

        // Close the mobile menu when the focus moves away from the last item in the top level
        if (this.lastMenuItem === null) {
            return;
        }

        this.lastMenuItem.addEventListener('focusout', () => {
            if (this.state.open) {
                this.close();
                this.state.open = false;
            }
        });
    }

    open() {
        // Fire a custom event which is useful if we need any other items such as
        // a search box to close when the mobile menu opens
        // Can be listened to with
        // document.addEventListener('onMenuOpen', () => {
        //     // do stuff here...;
        // });
        const menuOpenEvent = new Event('onMenuOpen');
        document.dispatchEvent(menuOpenEvent);
        this.node.setAttribute('aria-expanded', 'true');
        this.body.classList.add('no-scroll');
        this.primaryMobileMenu.classList.add('is-visible');

        this.state.open = true;
    }

    close() {
        this.node.setAttribute('aria-expanded', 'false');
        this.body.classList.remove('no-scroll');
        this.primaryMobileMenu.classList.remove('is-visible');

        this.state.open = false;
    }
}

export default PrimaryMobileMenu;
