import MobileMenu from './mobile-menu';

// todo: update markup when navigation is implemented

describe('MobileMenu', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button class="button button-menu-toggle" data-mobile-menu-toggle />
            <div class="header__menus header__menus--mobile" data-mobile-menu />
        `;
    });

    it('hides the menu by default', () => {
        // eslint-disable-next-line no-new
        new MobileMenu(document.querySelector(MobileMenu.selector()));

        expect(document.querySelector('[data-mobile-menu]').className).toBe(
            'header__menus header__menus--mobile',
        );
    });

    it('shows the menu when clicked', () => {
        // eslint-disable-next-line no-new
        new MobileMenu(document.querySelector(MobileMenu.selector()));

        const button = document.querySelector('[data-mobile-menu-toggle]');
        button.dispatchEvent(new Event('click'));

        expect(button.className).toBe('button button-menu-toggle is-open');
    });

    it('hides then menu when clicked once open', () => {
        // eslint-disable-next-line no-new
        new MobileMenu(document.querySelector(MobileMenu.selector()), () => {});

        const button = document.querySelector('[data-mobile-menu-toggle]');
        button.dispatchEvent(new Event('click'));
        button.dispatchEvent(new Event('click'));

        expect(button.className).toBe('button button-menu-toggle');
    });
});
