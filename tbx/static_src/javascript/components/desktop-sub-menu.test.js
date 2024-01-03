import DesktopSubMenu from './desktop-sub-menu';

describe('DesktopSubMenu', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div data-desktop-menu="">
                <nav aria-label="Primary">
                    <ul class="primary-nav" data-primary-nav="">
                        <li class="primary-nav__item primary-nav__item--is-parent" data-has-subnav="">
                            <a class="primary-nav__link" data-open-subnav="" href="/test-3-index/" aria-haspopup="true" aria-expanded="false">
                                Test index
                                <span class="primary-nav__icon">›</span>
                            </a>
                            <ul class="sub-nav">
                                <li class="sub-nav__item sub-nav__item--back" data-subnav-back="">‹ Back</li>
                                <li class="sub-nav__item">
                                    <a class="sub-nav__link" href="/test-3-index/">Overview</a>
                                </li>
                            </ul>
                        </li>
                        <li class="primary-nav__item primary-nav__item--is-parent" data-has-subnav="">
                            <a class="primary-nav__link" data-open-subnav="" href="/test-3-index/" aria-haspopup="true" aria-expanded="false">
                                Test index 2
                                <span class="primary-nav__icon">›</span>
                            </a>
                            <ul class="sub-nav">
                                <li class="sub-nav__item sub-nav__item--back" data-subnav-back="">‹ Back</li>
                                <li class="sub-nav__item">
                                    <a class="sub-nav__link" href="/test-3-index/">Overview</a>
                                </li>
                            </ul>
                        </li>
                    </ul>
                </nav>
            </div>
        `;
    });

    it('hides the dropdown menu by default', () => {
        // eslint-disable-next-line no-new
        new DesktopSubMenu(document.querySelector(DesktopSubMenu.selector()));

        expect(
            document.querySelector('[data-desktop-menu] [data-has-subnav]')
                .className,
        ).not.toContain('active');
        expect(
            document
                .querySelector('[data-desktop-menu] [data-open-subnav]')
                .getAttribute('aria-expanded'),
        ).toBe('false');
    });

    it('opens the menu when clicked', () => {
        const desktopSubMenu = new DesktopSubMenu(
            document.querySelectorAll(DesktopSubMenu.selector())[0],
        );

        const element = desktopSubMenu.node;
        element.dispatchEvent(new Event('click'));

        expect(
            document.querySelector('[data-desktop-menu] [data-has-subnav]')
                .className,
        ).toContain('active');
        expect(
            document
                .querySelector('[data-desktop-menu] [data-open-subnav]')
                .getAttribute('aria-expanded'),
        ).toBe('true');
    });

    it('closes the menu when clicked again', () => {
        const desktopSubMenu = new DesktopSubMenu(
            document.querySelectorAll(DesktopSubMenu.selector())[0],
        );

        const element = desktopSubMenu.node;
        element.dispatchEvent(new Event('click'));
        expect(
            document.querySelector('[data-desktop-menu] [data-has-subnav]')
                .className,
        ).toContain('active');
        expect(
            document
                .querySelector('[data-desktop-menu] [data-open-subnav]')
                .getAttribute('aria-expanded'),
        ).toBe('true');

        element.dispatchEvent(new Event('click'));

        expect(
            document.querySelector('[data-desktop-menu] [data-has-subnav]')
                .className,
        ).not.toContain('active');
        expect(
            document
                .querySelector('[data-desktop-menu] [data-open-subnav]')
                .getAttribute('aria-expanded'),
        ).toBe('false');
    });

    it('closes other menu items when clicked', () => {
        const desktopSubMenu1 = new DesktopSubMenu(
            document.querySelectorAll(DesktopSubMenu.selector())[0],
        );

        const desktopSubMenu2 = new DesktopSubMenu(
            document.querySelectorAll(DesktopSubMenu.selector())[1],
        );

        const element1 = desktopSubMenu1.node;
        const element2 = desktopSubMenu2.node;

        element1.dispatchEvent(new Event('click'));
        element2.dispatchEvent(new Event('click'));

        expect(
            document.querySelectorAll(
                '[data-desktop-menu] [data-has-subnav]',
            )[0].className,
        ).not.toContain('active');
        expect(
            document
                .querySelector('[data-desktop-menu] [data-open-subnav]')
                .getAttribute('aria-expanded'),
        ).toBe('false');
    });
});
