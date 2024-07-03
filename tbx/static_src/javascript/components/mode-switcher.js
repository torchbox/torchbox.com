import Cookies from 'js-cookie';

const { ALLOWED_MODES } = window.GLOBALS;

class ModeSwitcher {
    static selector() {
        return '[data-mode-switcher]';
    }

    constructor(node) {
        this.node = node;
        this.window = window;
        this.html = document.querySelector('html');
        this.modeRadios = node.querySelectorAll('[data-mode-switch]');

        let { mode } = this.html.dataset;

        // check for invalid mode values
        if (!ALLOWED_MODES.includes(mode)) mode = '';

        // if mode cookie is not set, use dark by default, otherwise use the cookie value
        this.mode = mode === '' ? 'dark' : mode;

        this.toggleMode();
        this.bindEventListeners();
    }

    bindEventListeners() {
        this.modeRadios.forEach((radio) => {
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    const mode = radio.value;
                    if (mode === this.mode) return;
                    this.mode = mode;
                    this.toggleMode();
                }
            });
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
        });
    }
}

export default ModeSwitcher;
