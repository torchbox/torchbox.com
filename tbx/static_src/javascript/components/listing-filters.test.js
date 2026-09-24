import ListingFilters from './listing-filters';

describe('ListingFilters', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <form data-listing-filters>
                <details id="d1" data-listing-filters-dropdown><summary>Sector</summary><label><input type="checkbox"></label></details>
                <details id="d2" data-listing-filters-dropdown><summary>Service</summary><label><input type="checkbox"></label></details>
            </form>
            <a href="/" id="outside">Outside</a>
        `;
        // eslint-disable-next-line no-new
        new ListingFilters(document.querySelector(ListingFilters.selector()));
    });

    it('closes an open dropdown when clicking outside it', () => {
        const dropdown = document.getElementById('d1');
        dropdown.open = true;

        document
            .getElementById('outside')
            .dispatchEvent(new Event('click', { bubbles: true }));

        expect(dropdown.open).toBe(false);
    });

    it('keeps a dropdown open when clicking inside it', () => {
        const dropdown = document.getElementById('d1');
        dropdown.open = true;

        dropdown
            .querySelector('input')
            .dispatchEvent(new Event('click', { bubbles: true }));

        expect(dropdown.open).toBe(true);
    });

    it('closes on Escape and returns focus to the summary', () => {
        const dropdown = document.getElementById('d1');
        dropdown.open = true;

        document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));

        expect(dropdown.open).toBe(false);
        expect(document.activeElement).toBe(dropdown.querySelector('summary'));
    });

    it('closes other dropdowns when one is opened', () => {
        const first = document.getElementById('d1');
        const second = document.getElementById('d2');
        first.open = true;
        second.open = true;

        second.dispatchEvent(new Event('toggle'));

        expect(first.open).toBe(false);
        expect(second.open).toBe(true);
    });
});

describe('ListingFilters with HTMX', () => {
    const pill = (param, value) =>
        `<li><a href="/?${param}=${value}" data-listing-filters-pill data-param="${param}" data-value="${value}"><span>${value}</span></a></li>`;

    const activeFilters = (pills) =>
        pills.length
            ? `<ul>${pills.map(([param, value]) => pill(param, value)).join('')}</ul>
               <a href="/" data-listing-filters-clear>Clear all filters</a>`
            : '';

    let form;
    let changeCount;

    // Stands in for the HTMX response: re-render the pills, then settle.
    const swapActiveFilters = (pills) => {
        document.getElementById('listing-active-filters').innerHTML =
            activeFilters(pills);
        document
            .getElementById('listing-results')
            .dispatchEvent(new Event('htmx:afterSettle', { bubbles: true }));
    };

    const clickPill = (param, value) => {
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
        });
        document
            .querySelector(`[data-param="${param}"][data-value="${value}"]`)
            .querySelector('span')
            .dispatchEvent(event);
        return event;
    };

    const checkbox = (name, value) =>
        form.querySelector(`input[name="${name}"][value="${value}"]`);

    beforeEach(() => {
        document.body.innerHTML = `
            <form data-listing-filters>
                <details data-listing-filters-dropdown>
                    <summary id="first-summary">Sector</summary>
                    <input type="checkbox" name="sector" value="charity" checked>
                    <input type="checkbox" name="sector" value="health" checked>
                </details>
                <details data-listing-filters-dropdown>
                    <summary>Service</summary>
                    <input type="checkbox" name="service" value="design" checked>
                </details>
                <button type="submit" data-listing-filters-submit>Apply filters</button>
                <div id="listing-active-filters">
                    ${activeFilters([
                        ['sector', 'charity'],
                        ['sector', 'health'],
                        ['service', 'design'],
                    ])}
                </div>
            </form>
            <ul id="listing-results"></ul>
        `;
        form = document.querySelector(ListingFilters.selector());
        changeCount = 0;
        form.addEventListener('change', () => {
            changeCount += 1;
        });
        // eslint-disable-next-line no-new
        new ListingFilters(form);
    });

    it('hides the submit button', () => {
        expect(
            form.querySelector('[data-listing-filters-submit]').classList,
        ).toContain('listing-filters__submit-button--hidden');
    });

    it('removes a pill filter without following the link', () => {
        const event = clickPill('sector', 'health');

        expect(event.defaultPrevented).toBe(true);
        expect(checkbox('sector', 'health').checked).toBe(false);
        expect(checkbox('sector', 'charity').checked).toBe(true);
        expect(checkbox('service', 'design').checked).toBe(true);
        expect(changeCount).toBe(1);
    });

    it('lets modified clicks on a pill follow the link', () => {
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            metaKey: true,
        });
        document
            .querySelector('[data-listing-filters-pill]')
            .dispatchEvent(event);

        expect(event.defaultPrevented).toBe(false);
        expect(checkbox('sector', 'charity').checked).toBe(true);
        expect(changeCount).toBe(0);
    });

    it('handles pills that were swapped in after init', () => {
        swapActiveFilters([['service', 'design']]);

        clickPill('service', 'design');

        expect(checkbox('service', 'design').checked).toBe(false);
        expect(changeCount).toBe(1);
    });

    it('clears every filter with one change', () => {
        const event = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
        });
        form.querySelector('[data-listing-filters-clear]').dispatchEvent(event);

        expect(event.defaultPrevented).toBe(true);
        expect(
            Array.from(form.querySelectorAll('input')).some(
                (input) => input.checked,
            ),
        ).toBe(false);
        expect(changeCount).toBe(1);
    });

    it('moves focus to the next pill after removing a pill', () => {
        clickPill('sector', 'health');
        swapActiveFilters([
            ['sector', 'charity'],
            ['service', 'design'],
        ]);

        expect(document.activeElement.dataset.value).toBe('design');
    });

    it('moves focus to the previous pill after removing the last pill', () => {
        clickPill('service', 'design');
        swapActiveFilters([
            ['sector', 'charity'],
            ['sector', 'health'],
        ]);

        expect(document.activeElement.dataset.value).toBe('health');
    });

    it('moves focus to the first dropdown after removing the only pill', () => {
        swapActiveFilters([['sector', 'charity']]);

        clickPill('sector', 'charity');
        swapActiveFilters([]);

        expect(document.activeElement.id).toBe('first-summary');
    });

    it('moves focus to the first dropdown after clearing all filters', () => {
        form.querySelector('[data-listing-filters-clear]').click();
        swapActiveFilters([]);

        expect(document.activeElement.id).toBe('first-summary');
    });

    it('leaves focus alone if a checkbox changes before the swap', () => {
        clickPill('sector', 'health');
        const other = checkbox('sector', 'charity');
        other.focus();
        other.dispatchEvent(new Event('change', { bubbles: true }));
        swapActiveFilters([['service', 'design']]);

        expect(document.activeElement).toBe(other);
    });

    it('marks the results as busy while a request is in flight', () => {
        const results = document.getElementById('listing-results');

        form.dispatchEvent(new Event('htmx:beforeRequest', { bubbles: true }));
        expect(results.getAttribute('aria-busy')).toBe('true');

        form.dispatchEvent(new Event('htmx:afterRequest', { bubbles: true }));
        expect(results.hasAttribute('aria-busy')).toBe(false);
    });
});
