/**
 * Progressive enhancement for the native <details> listing-filter dropdowns.
 *
 * The dropdowns work without JavaScript (open/close via <summary>). This adds
 * the two behaviours native <details> can't: closing when you click outside an
 * open dropdown, and closing on Escape (returning focus to its summary). Opening
 * one dropdown also closes any other open one.
 */
class ListingFilters {
    static selector() {
        return '[data-listing-filters]';
    }

    constructor(node) {
        this.node = node;
        this.dropdowns = Array.from(node.querySelectorAll('details'));
        this.bindEventListeners();
    }

    bindEventListeners() {
        // Close sibling dropdowns when one is opened.
        this.dropdowns.forEach((dropdown) => {
            dropdown.addEventListener('toggle', () => {
                if (dropdown.open) {
                    this.closeAll(dropdown);
                }
            });
        });

        document.addEventListener('click', (event) => this.handleClick(event));
        document.addEventListener('keydown', (event) => this.handleKeydown(event));
    }

    closeAll(except) {
        this.dropdowns.forEach((dropdown) => {
            if (dropdown !== except) {
                dropdown.open = false;
            }
        });
    }

    handleClick(event) {
        this.dropdowns.forEach((dropdown) => {
            if (dropdown.open && !dropdown.contains(event.target)) {
                dropdown.open = false;
            }
        });
    }

    handleKeydown(event) {
        if (event.key !== 'Escape') {
            return;
        }

        const openDropdown = this.dropdowns.find((dropdown) => dropdown.open);
        if (!openDropdown) {
            return;
        }

        openDropdown.open = false;
        const summary = openDropdown.querySelector('summary');
        if (summary) {
            summary.focus();
        }
    }
}

export default ListingFilters;
