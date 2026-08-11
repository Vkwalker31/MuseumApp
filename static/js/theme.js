/**
 * Переключатель темы светлая/тёмная (ЛР3, задание 2).
 * Сохраняет выбор в localStorage.
 */
(function () {
    const STORAGE_KEY = 'museum-theme';

    function applyTheme(theme) {
        const isDark = theme === 'dark';
        document.body.dataset.theme = theme;
        document.documentElement.dataset.theme = theme;
        document.body.classList.toggle('dark-theme', isDark);
        document.documentElement.classList.toggle('dark-theme', isDark);
        document.body.classList.toggle('night-mode', isDark);
        document.documentElement.classList.toggle('night-mode', isDark);
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            toggle.checked = isDark;
            toggle.setAttribute('aria-checked', isDark ? 'true' : 'false');
        }
    }

    function initTheme() {
        const saved = localStorage.getItem(STORAGE_KEY);
        applyTheme(saved === 'dark' ? 'dark' : 'light');
    }

    function toggleTheme() {
        const current = document.body.dataset.theme || 'light';
        const next = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem(STORAGE_KEY, next);
        applyTheme(next);
    }

    initTheme();

    document.addEventListener('DOMContentLoaded', () => {
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            toggle.addEventListener('change', toggleTheme);
        }
    });
})();
