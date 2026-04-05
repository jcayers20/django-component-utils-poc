document.addEventListener('DOMContentLoaded', () => {
    // Function to initialize logic for a single alert element
    const initAlert = (el) => {
        if (el.dataset.alertInitialized) return;

        // Mark as initialized to prevent double-init
        el.dataset.alertInitialized = 'true';

        // If auto-dismiss is enabled, wire up progress/timeout
        if (el.dataset.inputAutodismiss === 'true') {
            const delayMs = parseInt(el.dataset.inputDelayMs || '0', 10);
            const progressBar = el.querySelector('.alert-progress');

            if (progressBar) {
                // when the animation completes, programmatically close the alert
                progressBar.addEventListener('animationend', () => {
                    const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
                    bsAlert.close();
                });
            } else if (delayMs > 0) {
                // fallback: use a timeout if there is no progress bar
                setTimeout(() => {
                    const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
                    bsAlert.close();
                }, delayMs);
            }
        }

        // Remove element from DOM when hidden/closed
        el.addEventListener('closed.bs.alert', () => {
            el.remove();
        });
    };

    // initialize any existing alerts on page load
    document.querySelectorAll('.alert').forEach(initAlert);

    // initialize new alerts as they are added to the DOM
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType !== 1) return; // skip non-element nodes

                // check if the added node itself is an alert
                if (node.classList && node.classList.contains('alert')) {
                    initAlert(node);
                }

                // check if the added node contains alerts
                const nestedAlerts = node.querySelectorAll && node.querySelectorAll('.alert');
                if (nestedAlerts && nestedAlerts.forEach) nestedAlerts.forEach(initAlert);
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});