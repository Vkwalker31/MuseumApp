/**
 * Класс слайдера изображений (ЛР3, задание 1).
 * Поддерживает: навигацию, пагинацию, автопрокрутку, подписи, счётчик.
 */
class ImageSlider {
    constructor(container, options = {}) {
        this.container = typeof container === 'string'
            ? document.querySelector(container)
            : container;
        if (!this.container) return;

        this.slides = options.slides || [];
        this.currentIndex = 0;
        this.loop = options.loop !== false;
        this.navs = options.navs !== false;
        this.pags = options.pags !== false;
        this.auto = options.auto !== false;
        this.delay = (options.delay || 5) * 1000;
        this.stopMouseHover = options.stopMouseHover !== false;
        this.timer = null;
        this.isHovered = false;

        this._buildDOM();
        this._bindEvents();
        this.goTo(0);
        if (this.auto) this.startAuto();
    }

    _buildDOM() {
        this.container.innerHTML = '';
        this.container.classList.add('image-slider');

        this.track = document.createElement('div');
        this.track.className = 'image-slider__track';

        this.slides.forEach((slide, i) => {
            const item = document.createElement('div');
            item.className = 'image-slider__slide';
            item.dataset.index = i;

            const link = document.createElement('a');
            link.href = slide.link || '#';
            link.className = 'image-slider__link';
            link.setAttribute('aria-label', slide.caption || `Слайд ${i + 1}`);

            const img = document.createElement('img');
            img.src = slide.src;
            img.alt = slide.alt || slide.caption || '';
            img.loading = i === 0 ? 'eager' : 'lazy';
            link.appendChild(img);

            if (slide.caption) {
                const cap = document.createElement('span');
                cap.className = 'image-slider__caption';
                cap.textContent = slide.caption;
                link.appendChild(cap);
            }

            item.appendChild(link);
            this.track.appendChild(item);
        });

        this.counter = document.createElement('div');
        this.counter.className = 'image-slider__counter';
        this.counter.setAttribute('aria-live', 'polite');

        this.container.appendChild(this.track);
        this.container.appendChild(this.counter);

        if (this.navs) {
            this.btnPrev = document.createElement('button');
            this.btnPrev.type = 'button';
            this.btnPrev.className = 'image-slider__nav image-slider__nav--prev';
            this.btnPrev.innerHTML = '&#8249;';
            this.btnPrev.setAttribute('aria-label', 'Предыдущий слайд');

            this.btnNext = document.createElement('button');
            this.btnNext.type = 'button';
            this.btnNext.className = 'image-slider__nav image-slider__nav--next';
            this.btnNext.innerHTML = '&#8250;';
            this.btnNext.setAttribute('aria-label', 'Следующий слайд');

            this.container.appendChild(this.btnPrev);
            this.container.appendChild(this.btnNext);
        }

        if (this.pags) {
            this.pagination = document.createElement('div');
            this.pagination.className = 'image-slider__pagination';
            this.slides.forEach((_, i) => {
                const dot = document.createElement('button');
                dot.type = 'button';
                dot.className = 'image-slider__dot';
                dot.dataset.index = i;
                dot.setAttribute('aria-label', `Перейти к слайду ${i + 1}`);
                this.pagination.appendChild(dot);
            });
            this.container.appendChild(this.pagination);
        }
    }

    _bindEvents() {
        if (this.btnPrev) {
            this.btnPrev.addEventListener('click', () => this.prev());
        }
        if (this.btnNext) {
            this.btnNext.addEventListener('click', () => this.next());
        }
        if (this.pagination) {
            this.pagination.addEventListener('click', (e) => {
                const dot = e.target.closest('.image-slider__dot');
                if (dot) this.goTo(parseInt(dot.dataset.index, 10));
            });
        }
        if (this.stopMouseHover && this.auto) {
            this.container.addEventListener('mouseenter', () => {
                this.isHovered = true;
                this.stopAuto();
            });
            this.container.addEventListener('mouseleave', () => {
                this.isHovered = false;
                this.startAuto();
            });
        }
    }

    goTo(index) {
        if (!this.slides.length) return;

        if (index < 0) {
            index = this.loop ? this.slides.length - 1 : 0;
        } else if (index >= this.slides.length) {
            index = this.loop ? 0 : this.slides.length - 1;
        }

        this.currentIndex = index;
        const offset = -index * 100;
        this.track.style.transform = `translateX(${offset}%)`;

        this.counter.textContent = `${index + 1} / ${this.slides.length}`;

        if (this.pagination) {
            this.pagination.querySelectorAll('.image-slider__dot').forEach((dot, i) => {
                dot.classList.toggle('image-slider__dot--active', i === index);
            });
        }

        this.container.querySelectorAll('.image-slider__slide').forEach((slide, i) => {
            slide.classList.toggle('image-slider__slide--active', i === index);
        });
    }

    next() {
        this.goTo(this.currentIndex + 1);
        if (this.auto) this.resetAuto();
    }

    prev() {
        this.goTo(this.currentIndex - 1);
        if (this.auto) this.resetAuto();
    }

    startAuto() {
        if (!this.auto) return;
        this.stopAuto();
        this.timer = setInterval(() => {
            if (!this.isHovered) {
                this.goTo(this.currentIndex + 1);
            }
        }, this.delay);
    }

    stopAuto() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    resetAuto() {
        this.stopAuto();
        this.startAuto();
    }

    setDelay(seconds) {
        const sec = Math.max(1, Math.min(30, parseFloat(seconds) || 5));
        this.delay = sec * 1000;
        if (this.auto) {
            this.resetAuto();
        }
    }

    setLoop(value) { this.loop = !!value; }
    setNavs(value) {
        this.navs = !!value;
        if (this.btnPrev) this.btnPrev.style.display = value ? '' : 'none';
        if (this.btnNext) this.btnNext.style.display = value ? '' : 'none';
    }
    setPags(value) {
        this.pags = !!value;
        if (this.pagination) this.pagination.style.display = value ? '' : 'none';
    }
    setAuto(value) {
        this.auto = !!value;
        if (value) this.startAuto();
        else this.stopAuto();
    }
    setStopMouseHover(value) { this.stopMouseHover = !!value; }
}

window.ImageSlider = ImageSlider;
