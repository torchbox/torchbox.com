import MobileMenu from './mobile-menu';

describe('MobileMenu', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button class="button-menu-toggle" data-mobile-menu-toggle />
            <nav aria-label="Main navigation" class="primary-nav primary-nav--mobile" data-mobile-menu />
        `;
    });

    it('hides the menu by default', () => {
        // eslint-disable-next-line no-new
        new MobileMenu(document.querySelector(MobileMenu.selector()));

        expect(document.querySelector('[data-mobile-menu]').className).toBe(
            'primary-nav primary-nav--mobile',
        );
    });

    it('shows the menu when clicked', () => {
        // eslint-disable-next-line no-new
        new MobileMenu(document.querySelector(MobileMenu.selector()));

        const button = document.querySelector('[data-mobile-menu-toggle]');
        button.dispatchEvent(new Event('click'));

        expect(button.className).toBe('button-menu-toggle is-open');
        expect(document.querySelector('[data-mobile-menu]').className).toBe(
            'primary-nav primary-nav--mobile is-visible',
        );
    });

    it('hides then menu when clicked once open', () => {
        // eslint-disable-next-line no-new
        new MobileMenu(document.querySelector(MobileMenu.selector()), () => {});

        const button = document.querySelector('[data-mobile-menu-toggle]');
        button.dispatchEvent(new Event('click'));
        button.dispatchEvent(new Event('click'));

        expect(button.className).toBe('button-menu-toggle');
    });
});
