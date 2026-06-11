import HeaderSearch from './header-search';

describe('HeaderSearch', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button data-header-search-toggle aria-expanded="false" aria-label="Search site"></button>
            <div data-header-search-overlay aria-hidden="true">
                <button data-header-search-close aria-label="Close search"></button>
                <div class="header-search-overlay__panel">
                    <form class="header-search-overlay__form">
                        <input data-header-search-input type="search" />
                    </form>
                </div>
            </div>
        `;
    });

    it('opens the overlay and focuses the input', () => {
        jest.spyOn(window, 'requestAnimationFrame').mockImplementation(
            (callback) => {
                callback();
                return 0;
            },
        );

        const search = new HeaderSearch(
            document.querySelector('[data-header-search-overlay]'),
        );
        const toggle = document.querySelector('[data-header-search-toggle]');
        const input = document.querySelector('[data-header-search-input]');
        const focusSpy = jest.spyOn(input, 'focus');

        toggle.dispatchEvent(new Event('click'));

        expect(
            document.querySelector('[data-header-search-overlay]').className,
        ).toBe('is-visible');
        expect(toggle.getAttribute('aria-expanded')).toBe('true');
        expect(focusSpy).toHaveBeenCalled();
        search.close();
    });

    it('closes the overlay when clicking outside the form', () => {
        const search = new HeaderSearch(
            document.querySelector('[data-header-search-overlay]'),
        );
        const toggle = document.querySelector('[data-header-search-toggle]');
        const backdrop = document.querySelector('[data-header-search-close]');

        toggle.dispatchEvent(new Event('click'));
        backdrop.dispatchEvent(new Event('click'));

        expect(
            document.querySelector('[data-header-search-overlay]').className,
        ).toBe('');
        expect(toggle.getAttribute('aria-expanded')).toBe('false');
        search.close();
    });

    it('closes the overlay when Escape is pressed', () => {
        const search = new HeaderSearch(
            document.querySelector('[data-header-search-overlay]'),
        );
        const toggle = document.querySelector('[data-header-search-toggle]');
        const input = document.querySelector('[data-header-search-input]');

        toggle.dispatchEvent(new Event('click'));
        input.dispatchEvent(
            new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
        );

        expect(
            document.querySelector('[data-header-search-overlay]').className,
        ).toBe('');
        expect(toggle.getAttribute('aria-expanded')).toBe('false');
    });

    it('closes the overlay when the search toggle is clicked again', () => {
        const search = new HeaderSearch(
            document.querySelector('[data-header-search-overlay]'),
        );
        const toggle = document.querySelector('[data-header-search-toggle]');

        toggle.dispatchEvent(new Event('click'));
        toggle.dispatchEvent(new Event('click'));

        expect(
            document.querySelector('[data-header-search-overlay]').className,
        ).toBe('');
        expect(toggle.getAttribute('aria-expanded')).toBe('false');
    });
});
