import { submitListingFilters } from './listing-filters';

describe('listing filters', () => {
    it('replaces the selected results wrapper without replacing filter controls', () => {
        document.body.innerHTML = `
            <div id="listing-panel">
                <form
                    action="/news/"
                    data-listing-filters
                    data-listing-filters-url="/news/"
                >
                    <input type="checkbox" name="sector" value="health" checked>
                </form>
                <div data-listing-results></div>
            </div>
        `;
        window.htmx = { ajax: jest.fn() };

        submitListingFilters(document.querySelector('[data-listing-filters]'));

        expect(window.htmx.ajax).toHaveBeenCalledWith(
            'GET',
            '/news/',
            expect.objectContaining({
                select: '[data-listing-results]',
                swap: 'outerHTML',
                target: '[data-listing-results]',
                values: { sector: ['health'] },
            }),
        );
    });
});
