// Assumes the following html structure
// See patterns/components/tabs-nav/tabs.html in the project styleguide
/* <div class="tabs" data-tab-set>
    <div class="tabs-nav" aria-label="Tabs">
        <div class="tabs-nav__layout grid">
            <div class="tabs-nav__container" role="tablist" aria-label="Tabs">

                <a id="tab-1" class="tab-nav-item tab-nav-item--active" href="#tab-tab-1" role="tab" aria-controls="tab-1" data-tab="tab-tab-1" aria-selected="true">
                    Tab 1
                </a>


                <a id="tab-2" class="tab-nav-item " href="#tab-tab-2" role="tab" aria-controls="tab-2" data-tab="tab-tab-2" aria-selected="false">
                    Tab 2
                </a>
            </div>
        </div>
    </div>

    <div class="tabs__panel" id="tab-tab-1" role="tabpanel" aria-labelledby="tab-1" data-tab-panel>
        <p>Test one</p>
    </div>

    <div class="tabs__panel tabs__panel--hidden" id="tab-tab-2" role="tabpanel" aria-labelledby="tab-2" data-tab-panel>
        <p>Test two</p>
    </div>
</div> */

class Tabs {
    static selector() {
        return '[data-tab-set]';
    }

    constructor(node) {
        this.tabset = node;
        this.allTabs = this.tabset.querySelectorAll('[data-tab]');
        this.allTabPanels = this.tabset.querySelectorAll('[data-tab-panel]');
        this.activeTabClass = 'tab-nav-item--active';
        this.inactiveTabPaneClass = 'tabs__panel--hidden';
        this.updateHistory = false; // change to true if you would like a tab change to update the url and page history
        this.setActiveHashTab();

        this.bindEvents();
    }

    removeActive() {
        this.allTabs.forEach((tab) => {
            tab.classList.remove(this.activeTabClass);
            tab.setAttribute('aria-selected', 'false');
        });

        this.allTabPanels.forEach((tabPanel) => {
            tabPanel.classList.add(this.inactiveTabPaneClass);
        });
    }

    setActiveHashTab() {
        let path = window.location.href.split('#')[1];
        // If the user goes back to the first tab with the back button,
        // path will be undefined, so manually set it to tab-tab-1
        if (!path) {
            path = 'tab-tab-1';
        }

        this.allTabPanels.forEach((tabPanel) => {
            // Check if path hash matchs any of the tab ids
            if (path === tabPanel.id) {
                const targetPanel = this.tabset.querySelector(`#${path}`);
                const targetTab = this.tabset.querySelector(
                    `[data-tab='${path}']`,
                );
                this.setSelected(targetTab, targetPanel);
            }
        });
    }

    bindEvents() {
        this.allTabs.forEach((tab) => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const panelID = tab.dataset.tab;
                const targetPanel = document.querySelector(`#${panelID}`);

                if (this.updateHistory) {
                    // update the hash in the url
                    window.history.pushState({}, '', `#${panelID}`);
                }
                this.setSelected(tab, targetPanel);
                targetPanel.scrollIntoView();
            });
        });

        if (this.updateHistory) {
            // listen for the updated url hash and update the active tab
            window.addEventListener('hashchange', () => {
                this.setActiveHashTab();
            });
        }
    }

    setSelected(tab, tabPanel) {
        this.removeActive();
        tab.setAttribute('aria-selected', 'true');
        tab.classList.add(this.activeTabClass);
        tabPanel.classList.remove(this.inactiveTabPaneClass);
    }
}

export default Tabs;
