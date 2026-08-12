/**
 * Клиентская пагинация каталога услуг (ЛР3, задание 5).
 */
class CatalogPagination {
    constructor(options) {
        this.items = options.items || [];
        this.container = document.getElementById(options.containerId || 'catalog-cards');
        this.paginationEl = document.getElementById(options.paginationId || 'catalog-pagination');
        this.perPageSelect = document.getElementById('catalog-per-page');
        this.perPage = parseInt(this.perPageSelect?.value, 10) || 3;
        this.page = 1;
        this.renderCard = options.renderCard || this._defaultRender;

        this.perPageSelect?.addEventListener('change', () => {
            this.perPage = parseInt(this.perPageSelect.value, 10) || 3;
            this.page = 1;
            this.render();
        });

        this.render();
    }

    _defaultRender(item) {
        return `
            <article class="catalog-card card-3d" data-id="${item.id}">
                <a href="${item.url}">
                    ${item.image ? `<img src="${item.image}" alt="${item.name}" width="200" height="130" loading="lazy">` : ''}
                    <h3>${item.name}</h3>
                    <p>${item.description || ''}</p>
                    <data value="${item.price}">${item.price} BYN</data>
                </a>
            </article>
        `;
    }

    render() {
        const totalPages = Math.max(1, Math.ceil(this.items.length / this.perPage));
        if (this.page > totalPages) this.page = totalPages;

        const start = (this.page - 1) * this.perPage;
        const pageItems = this.items.slice(start, start + this.perPage);

        this.container.innerHTML = pageItems.map((item) => this.renderCard(item)).join('');

        if (window.initCard3D) window.initCard3D(this.container);

        if (!this.paginationEl) return;
        let html = `<span class="catalog-page-info">Стр. ${this.page} из ${totalPages} (${this.items.length} услуг)</span>`;
        if (this.page > 1) html += `<button type="button" data-page="${this.page - 1}">←</button>`;
        for (let i = 1; i <= totalPages; i++) {
            html += `<button type="button" data-page="${i}" ${i === this.page ? 'class="active"' : ''}>${i}</button>`;
        }
        if (this.page < totalPages) html += `<button type="button" data-page="${this.page + 1}">→</button>`;
        this.paginationEl.innerHTML = html;

        this.paginationEl.querySelectorAll('button[data-page]').forEach((btn) => {
            btn.addEventListener('click', () => {
                this.page = parseInt(btn.dataset.page, 10);
                this.render();
            });
        });
    }
}

window.CatalogPagination = CatalogPagination;
