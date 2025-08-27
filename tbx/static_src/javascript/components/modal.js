import MicroModal from 'micromodal'; // es6 module

// Markup required
// Trigger:
// <button type="button" data-micromodal-trigger="iframe-embed-modal">Open</button>
//
// Modal:
// <div class="modal" id="iframe-embed-modal" aria-hidden="true">
//   <div class="modal__overlay" data-micromodal-close></div>
//   <div class="modal__container"
//        role="dialog"
//        aria-modal="true"
//        aria-labelledby="modal-title">
//     <header class="modal__header">
//          <h2 id="modal-title">Service enquiry</h2>
//          <button type="button" data-micromodal-close aria-label="Close dialog"></button>
//     </header>
//     <div class="modal__content">...</div>
//   </div>
// </div>

class Modal {
    static selector() {
        return '[data-micromodal-trigger]';
    }

    constructor() {
        if (typeof MicroModal !== 'undefined') {
            MicroModal.init({
                openTrigger: 'data-micromodal-trigger',
                disableScroll: true,
            });
        }

        Modal.bindEvents();
    }

    static bindEvents() {
        // Listen for clicks on the document instead of using micromodel default, which doesn't work with htmx
        document.body.addEventListener('click', Modal.handleEvent);
        document.body.addEventListener('touchstart', Modal.handleEvent);
        document.body.addEventListener('keydown', Modal.handleKeyDown);
    }

    static handleEvent(event) {
        const trigger = event.target.closest('[data-micromodal-trigger]');
        if (trigger) {
            event.preventDefault();
            event.stopPropagation(); // Stop the event from bubbling up

            // Get the modal ID and open the correct modal
            const modalId = trigger.getAttribute('data-micromodal-trigger');
            if (modalId && typeof MicroModal !== 'undefined') {
                MicroModal.show(modalId);
                // Ensure tabbing forward from iframes stays within the modal
                Modal.ensurePostIframeFocusTrap(modalId);
            }
        }

        // Close modal when clicking on close buttons
        const closeButton = event.target.closest('[data-micromodal-close]');
        if (closeButton) {
            const modal = closeButton.closest('.modal');
            if (modal) {
                MicroModal.close(modal.id); // Close the modal
            }
        }
    }

    // Prevent Enter from closing modal unless on button
    static handleKeyDown(event) {
        if (event.key === 'Enter') {
            const modal = event.target.closest('.modal');
            if (modal) {
                // Allow Enter on buttons and prevent it on everything else
                if (event.target.tagName !== 'BUTTON') {
                    event.preventDefault();
                    event.stopPropagation();
                }
            }
        }
    }

    // When a modal contains an iframe, browser-level tabbing inside the iframe
    // does not bubble key events to the parent, so focus-trap libraries
    // cannot reliably intercept the Tab press. Add a focus sentinel immediately
    // after the iframe that redirects focus to the Close button.
    static ensurePostIframeFocusTrap(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        const container = modal.querySelector('.modal__container');
        if (!container) return;

        const iframe = container.querySelector('iframe');
        if (!iframe) return;

        // Only add once per modal instance
        if (container.querySelector('.modal__focus-sentinel')) return;

        const sentinel = document.createElement('span');
        sentinel.tabIndex = 0;

        sentinel.addEventListener('focus', () => {
            const closeButton = modal.querySelector('[data-micromodal-close]');
            if (closeButton) {
                closeButton.focus();
            }
        });

        iframe.parentNode.insertBefore(sentinel, iframe.nextSibling);
    }
}

export default Modal;
