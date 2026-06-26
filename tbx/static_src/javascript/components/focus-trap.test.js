import { getFocusableElements, trapFocus } from './focus-trap';

const isMobileMenuTabbable = (element) => {
    const hiddenSubnav = element.closest('[data-primary-subnav]');

    if (hiddenSubnav && !hiddenSubnav.classList.contains('is-visible')) {
        return false;
    }

    return true;
};

describe('focus-trap', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button id="toggle">Menu</button>
            <nav id="menu">
                <a href="/about/">About</a>
                <a href="/contact/">Contact</a>
                <input type="hidden" value="hidden value">
                <div data-primary-subnav id="hidden-subnav">
                    <button>Hidden back</button>
                </div>
            </nav>
            <a href="/outside/">Outside</a>
        `;
    });

    describe('getFocusableElements', () => {
        it('returns focusable elements in document order across multiple roots', () => {
            const toggle = document.getElementById('toggle');
            const menu = document.getElementById('menu');

            expect(
                getFocusableElements([toggle, menu]).map(
                    (el) => el.textContent,
                ),
            ).toEqual(['Menu', 'About', 'Contact', 'Hidden back']);
        });

        it('excludes focusable elements when a custom tabbable filter rejects them', () => {
            const menu = document.getElementById('menu');

            expect(
                getFocusableElements([menu], isMobileMenuTabbable).map(
                    (el) => el.textContent,
                ),
            ).toEqual(['About', 'Contact']);
        });

        it('excludes hidden inputs', () => {
            const menu = document.getElementById('menu');

            expect(
                getFocusableElements([menu]).map((el) => el.textContent),
            ).toEqual(['About', 'Contact', 'Hidden back']);
        });

        it('includes focusable elements inside visible subnav panels', () => {
            document
                .getElementById('hidden-subnav')
                .classList.add('is-visible');

            const menu = document.getElementById('menu');

            expect(
                getFocusableElements([menu], isMobileMenuTabbable).map(
                    (el) => el.textContent,
                ),
            ).toEqual(['About', 'Contact', 'Hidden back']);
        });
    });

    describe('trapFocus', () => {
        it('wraps focus from the last element to the first on Tab', () => {
            const toggle = document.getElementById('toggle');
            const menu = document.getElementById('menu');
            const contact = menu.querySelector('a[href="/contact/"]');

            contact.focus();

            const event = new KeyboardEvent('keydown', {
                key: 'Tab',
                bubbles: true,
            });
            const preventDefault = jest.fn();
            event.preventDefault = preventDefault;

            trapFocus(event, [toggle, menu], {
                isTabbable: isMobileMenuTabbable,
            });

            expect(preventDefault).toHaveBeenCalled();
            expect(document.activeElement).toBe(toggle);
        });

        it('wraps focus from the first element to the last on Shift+Tab', () => {
            const toggle = document.getElementById('toggle');
            const menu = document.getElementById('menu');
            const contact = menu.querySelector('a[href="/contact/"]');

            toggle.focus();

            const event = new KeyboardEvent('keydown', {
                key: 'Tab',
                shiftKey: true,
                bubbles: true,
            });
            const preventDefault = jest.fn();
            event.preventDefault = preventDefault;

            trapFocus(event, [toggle, menu], {
                isTabbable: isMobileMenuTabbable,
            });

            expect(preventDefault).toHaveBeenCalled();
            expect(document.activeElement).toBe(contact);
        });

        it('pulls focus back into the trap when Tab is pressed outside it', () => {
            const toggle = document.getElementById('toggle');
            const menu = document.getElementById('menu');
            const outside = document.querySelector('a[href="/outside/"]');

            outside.focus();

            const event = new KeyboardEvent('keydown', {
                key: 'Tab',
                bubbles: true,
            });
            const preventDefault = jest.fn();
            event.preventDefault = preventDefault;

            trapFocus(event, [toggle, menu], {
                isTabbable: isMobileMenuTabbable,
            });

            expect(preventDefault).toHaveBeenCalled();
            expect(document.activeElement).toBe(toggle);
        });
    });
});
