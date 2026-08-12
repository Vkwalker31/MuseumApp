/**
 * Анимация статуй при скролле — приближение и увеличение (ЛР3, задание 11, вариант 9).
 */
(function () {
    function initScrollStatues() {
        const section = document.getElementById('scroll-statues');
        if (!section) return;

        const statues = section.querySelectorAll('.scroll-statue');
        if (!statues.length) return;

        let ticking = false;

        function update() {
            const vh = window.innerHeight;
            statues.forEach((statue) => {
                const rect = statue.getBoundingClientRect();
                const center = rect.top + rect.height / 2;
                const progress = 1 - Math.min(Math.max(center / vh, 0), 1);
                const scale = 0.5 + progress * 1.2;
                const translateZ = progress * 200;
                const opacity = 0.3 + progress * 0.7;
                statue.style.transform = `translateZ(${translateZ}px) scale(${scale})`;
                statue.style.opacity = opacity;
            });
            ticking = false;
        }

        function onScroll() {
            if (!ticking) {
                requestAnimationFrame(update);
                ticking = true;
            }
        }

        window.addEventListener('scroll', onScroll, { passive: true });
        update();
    }

    function initFadeOnScroll() {
        document.querySelectorAll('.scroll-fade-in').forEach((el) => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    el.classList.toggle('scroll-fade-in--visible', entry.isIntersecting);
                });
            }, { threshold: 0.2 });
            observer.observe(el);
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initScrollStatues();
        initFadeOnScroll();
    });
})();
