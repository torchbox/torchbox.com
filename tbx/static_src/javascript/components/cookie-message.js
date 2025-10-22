import Cookies from 'js-cookie';

class CookieWarning {
    static selector() {
        return '[data-cookie-message]';
    }

    static vwoSelector() {
        return '[data-vwo-loader]';
    }

    constructor(node) {
        this.messageContainer = node;
        this.optInButton = this.messageContainer.querySelector(
            '[data-cookie-opt-in]',
        );
        this.optOutButton = this.messageContainer.querySelector(
            '[data-cookie-opt-out]',
        );
        this.cookieName = 'torchbox-cookie';
        this.cookieDuration = 365;
        this.activeClass = 'active';
        this.inactiveClass = 'inactive';
        
        this.template = document.querySelector(CookieWarning.vwoSelector());
        this.templateInitiated = false;

        this.checkCookie();
        this.bindEvents();
    }

    checkCookie() {
        if (!this.messageContainer) {
            return;
        }

        // If cookie doesn't exists
        if (!Cookies.get(this.cookieName)) {
            this.messageContainer.classList.add(this.activeClass);
        }
    }

    applyCookie(event, cookieValue) {
        // prevent default link action
        event.preventDefault();
        // Add classes
        this.messageContainer.classList.remove(this.activeClass);
        this.messageContainer.classList.add(this.inactiveClass);
        // Set cookie
        Cookies.set(this.cookieName, cookieValue, {
            expires: this.cookieDuration,
        });
        if (cookieValue) {
            window.VWO.init(1);
            window.VWO.push(['optInVisitor']);
            if (!this.templateInitiated) {
                this.templateInitiated = true;
                this.template.after(this.template.content.cloneNode(true));
            }
        } else {
            window.VWO.init(3);
            window.VWO.push(['optOutVisitor']);
        }
    }

    bindEvents() {
        if (!this.optInButton) {
            return;
        }

        this.optInButton.addEventListener('click', (event) => {
            this.applyCookie(event, true);
        });

        this.optOutButton.addEventListener('click', (event) =>
            this.applyCookie(event, false),
        );
    }
}

export default CookieWarning;
