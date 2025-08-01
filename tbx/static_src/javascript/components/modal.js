import MicroModal from 'micromodal'; // es6 module

// Assumes a strcuture as follows
// <div class="modal" id="filters" aria-hidden="true">
//     <div class="modal__overlay" tabindex="-1" data-micromodal-close></div>
//     <div class="modal__container" role="dialog" aria-modal="true" aria-labelledby="modal-title" >
//         <header class="modal__header">
//             <h2 class="modal__heading heading heading--two" id="modal-title">Title<h2>
//             <div class="modal__close">
//                 {% include "atoms/icon_buttons/icon_button.html" with modifier="close" data="data-micromodal-close" aria='aria-label="Close modal"' %}
//             </div>
//         </header>
//         <main class="modal__content" id="filters-content">
//             Content
//         </main>
//         <footer class="modal__footer">
//             <button class="modal__btn" data-micromodal-close>Close</button>
//             </footer>
//     </div>
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
            }
        }

        // Close modal when clicking on close buttons
        const closeButton = event.target.closest(
            '[data-micromodal-close], [data-listing-submit]',
        );
        if (closeButton) {
            const modal = closeButton.closest('.modal');
            if (modal) {
                MicroModal.close(modal.id); // Close the modal
                document.body.style.overflow = ''; // Remove overflow hidden from body
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
}

export default Modal;
