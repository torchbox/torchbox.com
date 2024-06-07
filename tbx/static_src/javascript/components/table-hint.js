// Button to scroll a table at mobile.
// Used in conjunction with semi-opaque styling that is removed,
// along with the button, once the user has scrolled
// This identical to typed-table-hint.js, but due to limitations of the kit features we need to duplicate it.
// If you have both table types in your repo, you can rationalise this to a single file.
class TableHint {
    static selector() {
        return '[data-table-hint]';
    }

    constructor(node) {
        this.node = node;
        this.button = node.querySelector('[data-table-hint-button]');
        this.bindEvents();
    }

    bindEvents() {
        // Once the user scrolls, remove the button and hint and don't reshow them
        this.node.addEventListener('scroll', () => {
            if (this.node.scrollLeft > 0) {
                this.node.classList.add('is-scrolling');
            }
        });

        // Check if the user prefers reduced motion - only use smooth scroll if they don't
        const isReduced =
            window.matchMedia('(prefers-reduced-motion: reduce)').matches ===
            true;

        this.button.addEventListener('click', () => {
            this.node.scroll({
                top: 0,
                left: 500,
                behavior: isReduced ? 'auto' : 'smooth',
            });
        });
    }
}

export default TableHint;
