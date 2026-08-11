/**
 * Утилита прелоадера для асинхронных операций (ЛР3).
 */
class PreloaderUtil {
    constructor(overlayId) {
        this.overlay = document.getElementById(overlayId);
    }

    show() {
        if (this.overlay) {
            this.overlay.classList.add('preloader-overlay--visible');
            this.overlay.setAttribute('aria-hidden', 'false');
        }
    }

    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('preloader-overlay--visible');
            this.overlay.setAttribute('aria-hidden', 'true');
        }
    }

    async wrap(promise, minMs = 400) {
        const started = Date.now();
        this.show();
        try {
            return await promise;
        } finally {
            const elapsed = Date.now() - started;
            const wait = Math.max(0, minMs - elapsed);
            setTimeout(() => this.hide(), wait);
        }
    }
}

window.PreloaderUtil = PreloaderUtil;
