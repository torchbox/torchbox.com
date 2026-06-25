import PrimaryMobileMenu from './primary-mobile-menu';

describe('PrimaryMobileMenu', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button data-primary-mobile-menu-toggle class="button-menu-toggle" />
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

        expect(button.className).toBe('button-menu-toggle is-open');
        expect(
            document.querySelector('[data-primary-mobile-menu]').className,
        ).toBe('primary-nav-mobile is-visible');
    });

    it('hides the menu when clicked outside once open', () => {
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

    it('does not restore focus to the toggle when clicked outside', () => {
        document.body.innerHTML = `
            <button data-primary-mobile-menu-toggle class="button-menu-toggle">Menu</button>
            <nav aria-label="Main navigation" class="primary-nav-mobile" data-primary-mobile-menu>
                <a href="/about/">About</a>
            </nav>
            <button id="outside">Outside</button>
        `;

        // eslint-disable-next-line no-new
        new PrimaryMobileMenu(
            document.querySelector(PrimaryMobileMenu.selector()),
        );

        const button = document.querySelector(
            '[data-primary-mobile-menu-toggle]',
        );
        const outside = document.getElementById('outside');

        button.dispatchEvent(new Event('click'));
        outside.focus();
        outside.dispatchEvent(new Event('click', { bubbles: true }));

        expect(document.activeElement).toBe(outside);
        expect(button.getAttribute('aria-expanded')).toBe('false');
    });

    it('traps focus within the menu when open', () => {
        document.body.innerHTML = `
            <button data-primary-mobile-menu-toggle class="button-menu-toggle">Menu</button>
            <nav aria-label="Main navigation" class="primary-nav-mobile" data-primary-mobile-menu>
                <a href="/about/">About</a>
                <a href="/contact/">Contact</a>
            </nav>
            <a href="/outside/">Outside</a>
        `;

        // eslint-disable-next-line no-new
        new PrimaryMobileMenu(
            document.querySelector(PrimaryMobileMenu.selector()),
        );

        const button = document.querySelector(
            '[data-primary-mobile-menu-toggle]',
        );
        const contact = document.querySelector('a[href="/contact/"]');

        button.dispatchEvent(new Event('click'));
        contact.focus();

        document.dispatchEvent(
            new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }),
        );

        expect(document.activeElement).toBe(button);
    });

    it('traps focus within a visible subnav panel', () => {
        document.body.innerHTML = `
            <button data-primary-mobile-menu-toggle class="button-menu-toggle">Menu</button>
            <nav aria-label="Main navigation" class="primary-nav-mobile" data-primary-mobile-menu>
                <a href="/about/">About</a>
                <div id="services-subnav" data-primary-subnav class="is-visible">
                    <button data-primary-subnav-back>Back</button>
                    <a href="/services/design/">Design</a>
                </div>
            </nav>
        `;

        // eslint-disable-next-line no-new
        new PrimaryMobileMenu(
            document.querySelector(PrimaryMobileMenu.selector()),
        );

        const button = document.querySelector(
            '[data-primary-mobile-menu-toggle]',
        );
        const design = document.querySelector('a[href="/services/design/"]');
        const back = document.querySelector('[data-primary-subnav-back]');

        button.dispatchEvent(new Event('click'));
        design.focus();

        document.dispatchEvent(
            new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }),
        );

        expect(document.activeElement).toBe(back);
    });

    it('returns focus to the submenu trigger when Escape closes a subnav', () => {
        document.body.innerHTML = `
            <button data-primary-mobile-menu-toggle class="button-menu-toggle">Menu</button>
            <nav aria-label="Main navigation" class="primary-nav-mobile is-visible" data-primary-mobile-menu>
                <button
                    data-open-primary-subnav
                    aria-controls="services-subnav"
                    aria-expanded="true"
                >
                    Services
                </button>
                <div id="services-subnav" data-primary-subnav class="is-visible">
                    <button data-primary-subnav-back>Back</button>
                    <a href="/services/design/">Design</a>
                </div>
            </nav>
        `;

        const menu = new PrimaryMobileMenu(
            document.querySelector(PrimaryMobileMenu.selector()),
        );
        menu.state.open = true;

        const trigger = document.querySelector('[data-open-primary-subnav]');

        document.dispatchEvent(
            new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
        );

        expect(document.activeElement).toBe(trigger);
        expect(trigger.getAttribute('aria-expanded')).toBe('false');
        expect(
            document.querySelector('[data-primary-subnav]').classList.contains(
                'is-visible',
            ),
        ).toBe(false);
    });

    it('returns focus to the toggle when Escape closes the menu', () => {
        document.body.innerHTML = `
            <button data-primary-mobile-menu-toggle class="button-menu-toggle">Menu</button>
            <nav aria-label="Main navigation" class="primary-nav-mobile is-visible" data-primary-mobile-menu>
                <a href="/about/">About</a>
            </nav>
        `;

        const menu = new PrimaryMobileMenu(
            document.querySelector(PrimaryMobileMenu.selector()),
        );
        menu.state.open = true;

        const button = document.querySelector(
            '[data-primary-mobile-menu-toggle]',
        );

        document.dispatchEvent(
            new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
        );

        expect(document.activeElement).toBe(button);
        expect(button.getAttribute('aria-expanded')).toBe('false');
    });
});
