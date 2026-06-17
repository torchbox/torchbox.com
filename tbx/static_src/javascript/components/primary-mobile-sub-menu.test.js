import PrimaryMobileSubMenu from './primary-mobile-sub-menu';

describe('PrimaryMobileSubMenu', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <nav class="primary-nav-mobile" data-primary-mobile-menu>
                <button data-open-primary-subnav aria-expanded="false">Services</button>
                <div data-primary-subnav>
                    <button data-primary-subnav-back>Back</button>
                    <a href="/services/">Services</a>
                </div>
            </nav>
        `;
    });

    it('moves focus into the submenu when opened', () => {
        // eslint-disable-next-line no-new
        new PrimaryMobileSubMenu(
            document.querySelector(PrimaryMobileSubMenu.selector()),
        );

        document
            .querySelector('[data-open-primary-subnav]')
            .dispatchEvent(new Event('click'));

        expect(document.activeElement).toBe(
            document.querySelector('[data-primary-subnav-back]'),
        );
        expect(
            document
                .querySelector('[data-open-primary-subnav]')
                .getAttribute('aria-expanded'),
        ).toBe('true');
        expect(
            document.querySelector('[data-primary-mobile-menu]').className,
        ).toBe('primary-nav-mobile primary-nav-mobile--subnav-open');
    });

    it('returns focus to the trigger when closed', () => {
        // eslint-disable-next-line no-new
        new PrimaryMobileSubMenu(
            document.querySelector(PrimaryMobileSubMenu.selector()),
        );

        const trigger = document.querySelector('[data-open-primary-subnav]');
        trigger.dispatchEvent(new Event('click'));
        document
            .querySelector('[data-primary-subnav-back]')
            .dispatchEvent(new Event('click'));

        expect(document.activeElement).toBe(trigger);
        expect(trigger.getAttribute('aria-expanded')).toBe('false');
        expect(
            document.querySelector('[data-primary-mobile-menu]').className,
        ).toBe('primary-nav-mobile');
    });
});
