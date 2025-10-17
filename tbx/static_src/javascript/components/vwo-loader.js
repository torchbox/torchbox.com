const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
};

class VWOLoader {
    static selector() {
        return '[data-vwo-loader]';
    }

    constructor() {
        this.template = document.querySelector(VWOLoader.selector());
        if (!this.template) return;
        this.initiated = false;
        this.bindEvents();
    }

    bindEvents() {
        window.addEventListener('CassieSubmittedConsent', () =>
            this.toggleVWO(),
        );
    }

    toggleVWO() {
        const isEnabled = getCookie('VWOCookie') === 'Yes';
        if (isEnabled) {
            window.VWO.init(1);
            window.VWO.push(['optInVisitor']);
            if (!this.initiated) {
                this.initiated = true;
                // add the template contents after the template node
                this.template.after(this.template.content.cloneNode(true));
            }
        } else {
            window.VWO.init(3);
            window.VWO.push(['optOutVisitor']);
        }
    }
}

export default VWOLoader;
