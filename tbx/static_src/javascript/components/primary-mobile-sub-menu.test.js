import PrimaryMobileSubMenu from './primary-mobile-sub-menu';

describe('PrimaryMobileSubMenu', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <nav class="primary-nav-mobile" data-primary-mobile-menu>
                <button data-open-primary-subnav aria-expanded="false" aria-controls="primary-nav-mobile-dropdown-1">Services</button>
                <div id="primary-nav-mobile-dropdown-1" data-primary-subnav>
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

    it('loops focus from the last item back to the back button on Tab', () => {
        // eslint-disable-next-line no-new
        new PrimaryMobileSubMenu(
            document.querySelector(PrimaryMobileSubMenu.selector()),
        );

        document
            .querySelector('[data-open-primary-subnav]')
            .dispatchEvent(new Event('click'));

        const lastLink = document.querySelector('a[href="/services/"]');
        const back = document.querySelector('[data-primary-subnav-back]');
        lastLink.focus();

        const tabEvent = new KeyboardEvent('keydown', {
            key: 'Tab',
            bubbles: true,
            cancelable: true,
        });
        document.dispatchEvent(tabEvent);

        expect(tabEvent.defaultPrevented).toBe(true);
        expect(document.activeElement).toBe(back);
    });

    it('loops focus from the back button to the last item on Shift+Tab', () => {
        // eslint-disable-next-line no-new
        new PrimaryMobileSubMenu(
            document.querySelector(PrimaryMobileSubMenu.selector()),
        );

        document
            .querySelector('[data-open-primary-subnav]')
            .dispatchEvent(new Event('click'));

        const lastLink = document.querySelector('a[href="/services/"]');
        const back = document.querySelector('[data-primary-subnav-back]');
        back.focus();

        const tabEvent = new KeyboardEvent('keydown', {
            key: 'Tab',
            shiftKey: true,
            bubbles: true,
            cancelable: true,
        });
        document.dispatchEvent(tabEvent);

        expect(tabEvent.defaultPrevented).toBe(true);
        expect(document.activeElement).toBe(lastLink);
    });

    it('does not trap focus once the subnav is closed', () => {
        // eslint-disable-next-line no-new
        new PrimaryMobileSubMenu(
            document.querySelector(PrimaryMobileSubMenu.selector()),
        );

        const trigger = document.querySelector('[data-open-primary-subnav]');
        trigger.dispatchEvent(new Event('click'));
        document
            .querySelector('[data-primary-subnav-back]')
            .dispatchEvent(new Event('click'));

        const tabEvent = new KeyboardEvent('keydown', {
            key: 'Tab',
            bubbles: true,
            cancelable: true,
        });
        document.dispatchEvent(tabEvent);

        expect(tabEvent.defaultPrevented).toBe(false);
    });

    it('does not throw when aria-controls is missing', () => {
        document.body.innerHTML = `
            <nav class="primary-nav-mobile" data-primary-mobile-menu>
                <button data-open-primary-subnav aria-expanded="false">Services</button>
            </nav>
        `;

        expect(() => {
            // eslint-disable-next-line no-new
            new PrimaryMobileSubMenu(
                document.querySelector(PrimaryMobileSubMenu.selector()),
            );
        }).not.toThrow();
    });
});
