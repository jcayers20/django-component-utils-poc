document.addEventListener('DOMContentLoaded', () => {
    // Function to initialize logic for a single toast element
    const initToast = (el) => {
        if (el.dataset.toastInitialized) return;

        // Mark as initialized to prevent double-init
        el.dataset.toastInitialized = 'true';

        // Initialize Bootstrap toast
        const toast = new bootstrap.Toast(el);
        toast.show();

        // remove toast from DOM when it is hidden
        el.addEventListener('hidden.bs.toast', () => {
            el.remove();
        });

        // auto-dismiss logic
        if (el.dataset.inputAutodismiss === 'true') {
            const progressBar = el.querySelector('.toast-progress');
            if (progressBar) {
                // when the animation completes, hide then remove the toast
                progressBar.addEventListener('animationend', () => {
                    toast.hide();
                });
            }
        }
    };

    // initialize any existing toasts on page load
    document.querySelectorAll('.toast').forEach(initToast);

    // initialize new toasts as they are added to the DOM
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType !== 1) return; // skip non-element nodes

                // check if the added node itself is a toast
                if (node.classList.contains('toast')) {
                    initToast(node);
                }

                // check if the added node contains toasts
                const nestedToasts = node.querySelectorAll('.toast');
                nestedToasts.forEach(initToast);
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
