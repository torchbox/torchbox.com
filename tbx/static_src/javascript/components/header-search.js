class HeaderSearch {
    static selector() {
        return '[data-header-search-overlay]';
    }

    constructor(node) {
        this.overlay = node;
        this.input = this.overlay.querySelector('[data-header-search-input]');
        this.form = this.overlay.querySelector('.header-search-overlay__form');
        this.toggles = document.querySelectorAll('[data-header-search-toggle]');
        this.closeTriggers = this.overlay.querySelectorAll(
            '[data-header-search-close]',
        );
        this.isOpen = false;
        this.handleKeydown = this.handleKeydown.bind(this);

        this.bindEventListeners();
    }

    handleKeydown(event) {
        if (event.key === 'Escape' && this.isOpen) {
            event.preventDefault();
            this.close();
        }
    }

    bindEventListeners() {
        this.toggles.forEach((toggle) => {
            toggle.addEventListener('click', (event) => {
                event.preventDefault();
                if (this.isOpen) {
                    this.close();
                } else {
                    this.open();
                }
            });
        });

        this.closeTriggers.forEach((trigger) => {
            trigger.addEventListener('click', () => {
                this.close();
            });
        });

        this.overlay.addEventListener('click', (event) => {
            if (!this.isOpen) {
                return;
            }

            if (this.form && !this.form.contains(event.target)) {
                this.close();
            }
        });

        document.addEventListener('keydown', this.handleKeydown, true);

        document.addEventListener('onSearchOpen', () => {
            if (this.isOpen) {
                this.close();
            }
        });

        document.addEventListener('onMenuOpen', () => {
            if (this.isOpen) {
                this.close();
            }
        });
    }

    open() {
        const menuOpenEvent = new Event('onSearchOpen');
        document.dispatchEvent(menuOpenEvent);

        this.overlay.classList.add('is-visible');
        this.overlay.setAttribute('aria-hidden', 'false');
        this.toggles.forEach((toggle) => {
            toggle.setAttribute('aria-expanded', 'true');
            toggle.classList.add('is-active');
        });
        document.body.classList.add('no-scroll');
        this.isOpen = true;

        window.requestAnimationFrame(() => {
            if (this.input) {
                this.input.focus();
            }
        });
    }

    close() {
        this.overlay.classList.remove('is-visible');
        this.overlay.setAttribute('aria-hidden', 'true');
        this.toggles.forEach((toggle) => {
            toggle.setAttribute('aria-expanded', 'false');
            toggle.classList.remove('is-active');
        });
        document.body.classList.remove('no-scroll');
        this.isOpen = false;
    }
}

export default HeaderSearch;
