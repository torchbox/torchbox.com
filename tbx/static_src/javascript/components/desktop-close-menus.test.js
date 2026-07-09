import DesktopCloseMenus from './desktop-close-menus';
import PrimaryDesktopSubMenu from './primary-desktop-sub-menu';

describe('DesktopCloseMenus', () => {
    // DesktopCloseMenus binds document-level click/focusout/keydown
    // listeners for the lifetime of the page, so — as in production — it's
    // instantiated once here rather than per test. classList/aria state is
    // reset in beforeEach instead of recreating the DOM.
    beforeAll(() => {
        document.body.innerHTML = `
            <nav aria-label="Main navigation" class="primary-nav-desktop" data-primary-desktop-menu>
                <ul class="primary-nav-desktop__list">
                    <li class="primary-nav-desktop__item primary-nav-desktop__item--has-children" data-has-subnav>
                        <button
                            class="primary-nav-desktop__link primary-nav-desktop__link--has-children"
                            data-open-primary-subnav
                            aria-expanded="false"
                            aria-controls="primary-nav-dropdown-1"
                        >
                            Services
                        </button>
                        <div class="primary-nav-dropdown" id="primary-nav-dropdown-1" data-primary-subnav>
                            <a href="/services/design/" class="primary-nav-dropdown__row-link">Design</a>
                            <a href="/services/strategy/" class="primary-nav-dropdown__row-link">Strategy</a>
                        </div>
                    </li>
                </ul>
            </nav>
            <div class="primary-nav-dropdown-backdrop" data-primary-nav-dropdown-backdrop aria-hidden="true"></div>
            <main>
                <a href="/about/" id="page-content-link">About</a>
            </main>
        `;

        document
            .querySelectorAll(PrimaryDesktopSubMenu.selector())
            .forEach((node) => new PrimaryDesktopSubMenu(node));

        // eslint-disable-next-line no-new
        new DesktopCloseMenus();
    });

    beforeEach(() => {
        document.querySelector('[data-has-subnav]').classList.remove('active');
        document
            .querySelector('[data-open-primary-subnav]')
            .setAttribute('aria-expanded', 'false');
        document.body.classList.remove(
            'no-scroll',
            'primary-nav-dropdown-open',
        );
        document
            .querySelector('[data-primary-nav-dropdown-backdrop]')
            .setAttribute('aria-hidden', 'true');
        document.body.focus();
    });

    const openDropdown = () => {
        document
            .querySelector('[data-open-primary-subnav]')
            .dispatchEvent(new Event('click', { bubbles: true }));
    };

    it('opens the dropdown on click', () => {
        openDropdown();

        expect(document.querySelector('[data-has-subnav]').classList).toContain(
            'active',
        );
        expect(document.body.classList).toContain('primary-nav-dropdown-open');
    });

    it('closes the dropdown when focus tabs past the last link inside it', () => {
        openDropdown();

        const strategyLink = document.querySelector(
            'a[href="/services/strategy/"]',
        );
        const outsideLink = document.getElementById('page-content-link');
        strategyLink.focus();

        strategyLink.dispatchEvent(
            new FocusEvent('focusout', {
                bubbles: true,
                relatedTarget: outsideLink,
            }),
        );

        expect(
            document.querySelector('[data-has-subnav]').classList,
        ).not.toContain('active');
        expect(
            document
                .querySelector('[data-open-primary-subnav]')
                .getAttribute('aria-expanded'),
        ).toBe('false');
        expect(document.body.classList).not.toContain(
            'primary-nav-dropdown-open',
        );
        expect(document.body.classList).not.toContain('no-scroll');
        expect(
            document
                .querySelector('[data-primary-nav-dropdown-backdrop]')
                .getAttribute('aria-hidden'),
        ).toBe('true');
    });

    it('keeps the dropdown open when focus moves between links inside it', () => {
        openDropdown();

        const designLink = document.querySelector(
            'a[href="/services/design/"]',
        );
        const strategyLink = document.querySelector(
            'a[href="/services/strategy/"]',
        );
        designLink.focus();

        designLink.dispatchEvent(
            new FocusEvent('focusout', {
                bubbles: true,
                relatedTarget: strategyLink,
            }),
        );

        expect(document.querySelector('[data-has-subnav]').classList).toContain(
            'active',
        );
        expect(document.body.classList).toContain('primary-nav-dropdown-open');
    });

    it('closes the dropdown when clicking outside it', () => {
        openDropdown();

        document
            .getElementById('page-content-link')
            .dispatchEvent(new Event('click', { bubbles: true }));

        expect(
            document.querySelector('[data-has-subnav]').classList,
        ).not.toContain('active');
        expect(document.body.classList).not.toContain(
            'primary-nav-dropdown-open',
        );
    });

    it('closes the dropdown on Escape', () => {
        openDropdown();

        document.dispatchEvent(
            new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
        );

        expect(
            document.querySelector('[data-has-subnav]').classList,
        ).not.toContain('active');
    });
});
