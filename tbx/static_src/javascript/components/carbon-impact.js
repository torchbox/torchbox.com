class CarbonImpact {
    static selector() {
        return '[data-page-carbon]';
    }

    constructor(node) {
        this.pageCarbon = node;
        this.pageLoadSpeed = this.pageCarbon.querySelector('[data-page-load-speed]');
        
        this.bindEvents();
    }

    bindEvents() {
        window.addEventListener("load", () => {
            // if we're keeping load speed, this will need updating to use non-deprecated JS
            const loadTime = window.performance.timing.domContentLoadedEventEnd - window.performance.timing.navigationStart;
            const loadTimeInSeconds = loadTime / 1000;
            this.pageLoadSpeed.innerHTML = `${loadTimeInSeconds  }s`;
        });  
    }
}

export default CarbonImpact;
