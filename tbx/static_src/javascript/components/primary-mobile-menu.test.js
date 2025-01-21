import PrimaryMobileMenu from './primary-mobile-menu';

describe('MobileMenu', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button data-primary-mobile-menu-toggle />
            <nav aria-label="Main navigation" class="primary-nav-mobile" data-primary-mobile-menu />
        `;
    });

    it('hides the menu by default', () => {
        // eslint-disable-next-line no-new
        new PrimaryMobileMenu(
            document.querySelector(PrimaryMobileMenu.selector()),
        );

        expect(
            document.querySelector('[data-primary-mobile-menu]').className,
        ).toBe('primary-nav-mobile');
    });

    it('shows the menu when clicked', () => {
        // eslint-disable-next-line no-new
        new PrimaryMobileMenu(
            document.querySelector(PrimaryMobileMenu.selector()),
        );

        const button = document.querySelector(
            '[data-primary-mobile-menu-toggle]',
        );
        button.dispatchEvent(new Event('click'));

        expect(
            document.querySelector('[data-primary-mobile-menu]').className,
        ).toBe('primary-nav-mobile is-visible');
    });

    it('hides then menu when clicked outside once open', () => {
        // eslint-disable-next-line no-new
        new PrimaryMobileMenu(
            document.querySelector(PrimaryMobileMenu.selector()),
            () => {},
        );

        const button = document.querySelector(
            '[data-primary-mobile-menu-toggle]',
        );
        button.dispatchEvent(new Event('click'));
        expect(
            document.querySelector('[data-primary-mobile-menu]').className,
        ).toBe('primary-nav-mobile is-visible');

        document.dispatchEvent(new Event('click'));
        expect(
            document.querySelector('[data-primary-mobile-menu]').className,
        ).toBe('primary-nav-mobile');
    });
});
