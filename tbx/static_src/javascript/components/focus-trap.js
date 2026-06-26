const FOCUSABLE_SELECTOR = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled]):not([type="hidden"])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
].join(', ');

function isElementVisible(element) {
    let node = element;

    while (node) {
        const style = window.getComputedStyle(node);

        if (
            style.visibility === 'hidden' ||
            style.display === 'none' ||
            node.getAttribute('aria-hidden') === 'true'
        ) {
            return false;
        }

        node = node.parentElement;
    }

    return true;
}

function defaultIsTabbable(element) {
    if (element.disabled) {
        return false;
    }

    return isElementVisible(element);
}

export function getFocusableElements(roots, isTabbable = defaultIsTabbable) {
    const seen = new Set();
    const elements = [];

    document.querySelectorAll(FOCUSABLE_SELECTOR).forEach((element) => {
        const isInsideRoot = roots.some(
            (root) => root && (root === element || root.contains(element)),
        );

        if (isInsideRoot && isTabbable(element) && !seen.has(element)) {
            seen.add(element);
            elements.push(element);
        }
    });

    return elements;
}

export function trapFocus(event, roots, options = {}) {
    if (event.key !== 'Tab') {
        return;
    }

    const { isTabbable = defaultIsTabbable } = options;
    const focusable = getFocusableElements(roots, isTabbable);

    if (focusable.length === 0) {
        return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const active = document.activeElement;
    const activeIsInsideTrap = focusable.includes(active);

    if (event.shiftKey) {
        if (active === first || !activeIsInsideTrap) {
            event.preventDefault();
            last.focus();
        }

        return;
    }

    if (active === last || !activeIsInsideTrap) {
        event.preventDefault();
        first.focus();
    }
}
