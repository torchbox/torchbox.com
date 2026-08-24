import ListingFilters from './listing-filters';

describe('ListingFilters', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <form data-listing-filters>
                <details id="d1"><summary>Sector</summary><label><input type="checkbox"></label></details>
                <details id="d2"><summary>Service</summary><label><input type="checkbox"></label></details>
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
