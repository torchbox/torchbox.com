/**
 * Progressive enhancement for the listing-filter form.
 *
 * The dropdowns work without JavaScript (open/close via <summary>). This adds
 * the two behaviours native <details> can't: closing when you click outside an
 * open dropdown, and closing on Escape (returning focus to its summary). Opening
 * one dropdown also closes any other open one.
 *
 * HTMX re-requests the page whenever the form changes (see the hx-* attributes
 * in listing-filters.html), so this also hides the Apply button, and turns the
 * active-filter pills and "Clear all" link into checkbox changes instead of
 * page loads. Their hrefs remain the no-JS fallback.
 */
class ListingFilters {
    static selector() {
        return '[data-listing-filters]';
    }

    constructor(node) {
        this.node = node;
        this.dropdowns = Array.from(
            node.querySelectorAll('[data-listing-filters-dropdown]'),
        );
        this.submitButton = node.querySelector('[data-listing-filters-submit]');
        // Where to move focus once HTMX has swapped in the new pills: a
        // { param, value } pill, or null for the first dropdown toggle.
        this.pendingFocus = undefined;

        if (this.submitButton) {
            this.submitButton.classList.add(
                'listing-filters__submit-button--hidden',
            );
        }

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
        document.addEventListener('keydown', (event) =>
            this.handleKeydown(event),
        );

        // Delegated, because the pills are replaced on every swap.
        this.node.addEventListener('click', (event) =>
            this.handleRemoveClick(event),
        );

        // A checkbox changed by the user supersedes any pending pill removal,
        // so focus should stay on that checkbox.
        this.node.addEventListener('change', (event) => {
            if (event.target !== this.node) {
                this.pendingFocus = undefined;
            }
        });

        document.addEventListener('htmx:afterSettle', () =>
            this.restoreFocus(),
        );

        // The results list is looked up by id because that's how HTMX targets
        // it, and it's outside this component.
        this.node.addEventListener('htmx:beforeRequest', () => {
            const results = document.getElementById('listing-results');
            if (results) {
                results.setAttribute('aria-busy', 'true');
            }
        });
        this.node.addEventListener('htmx:afterRequest', () => {
            const results = document.getElementById('listing-results');
            if (results) {
                results.removeAttribute('aria-busy');
            }
        });
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

    handleRemoveClick(event) {
        // Let modified clicks open the link in a new tab or window.
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
            return;
        }

        const pill = event.target.closest('[data-listing-filters-pill]');
        const clear = event.target.closest('[data-listing-filters-clear]');
        if (!pill && !clear) {
            return;
        }

        event.preventDefault();

        if (pill) {
            const { param, value } = pill.dataset;
            this.checkboxes()
                .filter(
                    (input) => input.name === param && input.value === value,
                )
                .forEach((input) => {
                    input.checked = false;
                });
            this.pendingFocus = this.focusTargetAfterRemoving(pill);
        } else {
            this.checkboxes().forEach((input) => {
                input.checked = false;
            });
            this.pendingFocus = null;
        }

        this.node.dispatchEvent(new Event('change', { bubbles: true }));
    }

    checkboxes() {
        return Array.from(this.node.querySelectorAll('input[type="checkbox"]'));
    }

    pills() {
        return Array.from(
            this.node.querySelectorAll('[data-listing-filters-pill]'),
        );
    }

    focusTargetAfterRemoving(pill) {
        const pills = this.pills();
        const index = pills.indexOf(pill);
        const target = pills[index + 1] || pills[index - 1];
        return target
            ? { param: target.dataset.param, value: target.dataset.value }
            : null;
    }

    restoreFocus() {
        if (this.pendingFocus === undefined) {
            return;
        }

        const target = this.pendingFocus;
        this.pendingFocus = undefined;

        const pill =
            target &&
            this.pills().find(
                (element) =>
                    element.dataset.param === target.param &&
                    element.dataset.value === target.value,
            );
        const summary = this.node.querySelector(
            '[data-listing-filters-dropdown] summary',
        );
        const focusable = pill || summary;
        if (focusable) {
            focusable.focus();
        }
    }
}

export default ListingFilters;
