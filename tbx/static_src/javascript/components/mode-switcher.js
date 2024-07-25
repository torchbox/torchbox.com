import Cookies from 'js-cookie';

const { ALLOWED_MODES, BASE_DOMAIN } = window.GLOBALS;

class ModeSwitcher {
    static selector() {
        return '[data-mode-switcher]';
    }

    constructor(node) {
        this.node = node;
        this.window = window;
        this.html = document.querySelector('html');
        this.modeButton = node.querySelector('[data-mode-switch]');

        let { mode } = this.html.dataset;

        // check for invalid mode values
        if (!ALLOWED_MODES.includes(mode)) mode = '';

        // if torchbox-mode cookie is not set (it is passed via the data-mode attribute on the html tag), use dark by default - otherwise use the cookie value
        this.mode = mode === '' ? 'dark' : mode;

        this.bindEventListeners();
    }

    bindEventListeners() {
        this.modeButton.addEventListener('click', (event) => {
            event.preventDefault();
            this.mode = this.mode === 'dark' ? 'light' : 'dark';
            this.toggleMode();
        });

        this.node.querySelectorAll('form').forEach((form) => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
            });
        });
    }

    toggleMode() {
        ALLOWED_MODES.forEach((allowedMode) => {
            if (allowedMode !== this.mode) {
                this.html.classList.remove(`mode-${allowedMode}`);
            }
        });
        this.html.classList.add(`mode-${this.mode}`);
        this.html.dataset.mode = this.mode;
        Cookies.set('torchbox-mode', this.mode, {
            expires: 365,
            domain: BASE_DOMAIN,
        });
    }
}

export default ModeSwitcher;
