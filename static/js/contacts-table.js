/**
 * Интерактивная таблица контактов (ЛР3, задание 3).
 */
class ContactsTable {
    constructor(options) {
        this.apiUrl = options.apiUrl;
        this.tableBody = document.getElementById('contacts-tbody');
        this.tableHead = document.getElementById('contacts-thead');
        this.detailBlock = document.getElementById('contact-detail');
        this.bonusBlock = document.getElementById('bonus-result');
        this.filterInput = document.getElementById('contacts-filter');
        this.paginationEl = document.getElementById('contacts-pagination');
        this.addForm = document.getElementById('contact-add-form');
        this.addFormWrap = document.getElementById('contact-add-wrap');
        this.validationMsg = document.getElementById('validation-result');
        this.preloader = new PreloaderUtil('contacts-preloader');

        this.data = [];
        this.filtered = [];
        this.sortCol = 'name';
        this.sortDir = 'asc';
        this.page = 1;
        this.perPage = 3;
        this.nextId = 1000;

        this._bindUI();
        this.loadData();
    }

    _bindUI() {
        document.getElementById('btn-add-toggle')?.addEventListener('click', () => {
            this.addFormWrap.classList.toggle('contact-add-wrap--open');
        });

        document.getElementById('btn-filter')?.addEventListener('click', () => {
            this.page = 1;
            this.applyFilter();
        });

        document.getElementById('btn-bonus')?.addEventListener('click', () => {
            this.generateBonus();
        });

        this.tableHead?.addEventListener('click', (e) => {
            const th = e.target.closest('[data-sort]');
            if (!th) return;
            const col = th.dataset.sort;
            if (this.sortCol === col) {
                this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortCol = col;
                this.sortDir = 'asc';
            }
            this.render();
        });

        this.addForm?.querySelectorAll('input').forEach((input) => {
            input.addEventListener('input', () => this._validateAddForm());
        });

        document.getElementById('btn-add-submit')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.addRow();
        });
    }

    async loadData() {
        await this.preloader.wrap(
            fetch(this.apiUrl)
                .then((r) => r.json())
                .then((json) => {
                    this.data = json.contacts || [];
                    this.nextId = Math.max(...this.data.map((c) => c.id), 0) + 1;
                    this.applyFilter();
                })
                .catch(() => {
                    this.data = [];
                    this.applyFilter();
                })
        );
    }

    applyFilter() {
        const q = (this.filterInput?.value || '').trim().toLowerCase();
        if (!q) {
            this.filtered = [...this.data];
        } else {
            this.filtered = this.data.filter((row) =>
                ['name', 'role', 'phone', 'email', 'description'].some(
                    (k) => (row[k] || '').toLowerCase().includes(q)
                )
            );
        }
        this.render();
    }

    _sortData(rows) {
        const col = this.sortCol;
        const dir = this.sortDir === 'asc' ? 1 : -1;
        return [...rows].sort((a, b) => {
            const va = (a[col] || '').toString().toLowerCase();
            const vb = (b[col] || '').toString().toLowerCase();
            if (va < vb) return -1 * dir;
            if (va > vb) return 1 * dir;
            return 0;
        });
    }

    render() {
        const sorted = this._sortData(this.filtered);
        const totalPages = Math.max(1, Math.ceil(sorted.length / this.perPage));
        if (this.page > totalPages) this.page = totalPages;

        const start = (this.page - 1) * this.perPage;
        const pageRows = sorted.slice(start, start + this.perPage);

        this.tableHead.querySelectorAll('[data-sort]').forEach((th) => {
            const arrow = th.querySelector('.sort-arrow');
            if (th.dataset.sort === this.sortCol) {
                th.dataset.direction = this.sortDir;
                if (arrow) arrow.textContent = this.sortDir === 'asc' ? ' ▲' : ' ▼';
            } else {
                th.dataset.direction = '';
                if (arrow) arrow.textContent = '';
            }
        });

        this.tableBody.innerHTML = pageRows.map((row) => `
            <tr data-id="${row.id}" tabindex="0">
                <td><input type="checkbox" class="contact-check" data-id="${row.id}" aria-label="Выбрать ${row.name}"></td>
                <td>${this._esc(row.name)}</td>
                <td>${row.photo ? `<img src="${this._esc(row.photo)}" alt="" width="48" height="48" class="contact-thumb">` : '—'}</td>
                <td>${this._esc(row.role)}</td>
                <td>${this._esc(row.description)}</td>
                <td>${this._esc(row.phone)}</td>
                <td>${this._esc(row.email)}</td>
            </tr>
        `).join('');

        this.tableBody.querySelectorAll('tr').forEach((tr) => {
            tr.addEventListener('click', (e) => {
                if (e.target.type === 'checkbox') return;
                const id = parseInt(tr.dataset.id, 10);
                const row = this.data.find((r) => r.id === id);
                if (row) this.showDetail(row);
            });
        });

        this._renderPagination(totalPages);
    }

    _renderPagination(totalPages) {
        if (!this.paginationEl) return;
        let html = '';
        if (this.page > 1) {
            html += `<button type="button" data-page="${this.page - 1}">← Назад</button>`;
        }
        for (let i = 1; i <= totalPages; i++) {
            html += `<button type="button" data-page="${i}" class="${i === this.page ? 'active' : ''}">${i}</button>`;
        }
        if (this.page < totalPages) {
            html += `<button type="button" data-page="${this.page + 1}">Вперёд →</button>`;
        }
        this.paginationEl.innerHTML = html;
        this.paginationEl.querySelectorAll('button').forEach((btn) => {
            btn.addEventListener('click', () => {
                this.page = parseInt(btn.dataset.page, 10);
                this.render();
            });
        });
    }

    showDetail(row) {
        if (!this.detailBlock) return;
        this.detailBlock.innerHTML = `
            <h3>${this._esc(row.name)}</h3>
            <p><strong>Должность:</strong> ${this._esc(row.role)}</p>
            <p><strong>Описание:</strong> ${this._esc(row.description)}</p>
            <p><strong>Телефон:</strong> ${this._esc(row.phone)}</p>
            <p><strong>Email:</strong> ${this._esc(row.email)}</p>
            ${row.photo ? `<img src="${this._esc(row.photo)}" alt="${this._esc(row.name)}" width="120">` : ''}
        `;
        this.detailBlock.classList.add('contact-detail--visible');
    }

    _validateAddForm() {
        const name = document.getElementById('add-name')?.value.trim();
        const photo = document.getElementById('add-photo')?.value.trim();
        const role = document.getElementById('add-role')?.value.trim();
        const desc = document.getElementById('add-desc')?.value.trim();
        const phone = document.getElementById('add-phone')?.value.trim();
        const email = document.getElementById('add-email')?.value.trim();

        const photoEl = document.getElementById('add-photo');
        const phoneEl = document.getElementById('add-phone');

        const urlValid = validateUrl(photo);
        const phoneValid = validatePhone(phone);

        photoEl?.classList.toggle('field-invalid', photo && !urlValid);
        phoneEl?.classList.toggle('field-invalid', phone && !phoneValid);

        let msg = '';
        if (photo && !urlValid) msg += 'URL фото невалиден (http(s)://...*.php или *.html). ';
        if (phone && !phoneValid) msg += 'Номер телефона невалиден. ';
        if (photo && urlValid) msg += 'URL фото: OK. ';
        if (phone && phoneValid) msg += 'Телефон: OK. ';

        if (this.validationMsg) this.validationMsg.textContent = msg;

        const allFilled = name && photo && role && desc && phone && email;
        const btn = document.getElementById('btn-add-submit');
        if (btn) btn.disabled = !(allFilled && urlValid && phoneValid);
    }

    addRow() {
        const row = {
            id: this.nextId++,
            name: document.getElementById('add-name').value.trim(),
            photo: document.getElementById('add-photo').value.trim(),
            role: document.getElementById('add-role').value.trim(),
            description: document.getElementById('add-desc').value.trim(),
            phone: document.getElementById('add-phone').value.trim(),
            email: document.getElementById('add-email').value.trim(),
        };
        this.data.push(row);
        this.addForm.reset();
        document.getElementById('btn-add-submit').disabled = true;
        if (this.validationMsg) this.validationMsg.textContent = '';
        this.applyFilter();
        this.addFormWrap.classList.remove('contact-add-wrap--open');
    }

    generateBonus() {
        const checked = [...document.querySelectorAll('.contact-check:checked')];
        if (!checked.length) {
            if (this.bonusBlock) this.bonusBlock.textContent = 'Выберите сотрудников для премирования.';
            return;
        }
        const names = checked.map((cb) => {
            const id = parseInt(cb.dataset.id, 10);
            const row = this.data.find((r) => r.id === id);
            if (!row) return '';
            const parts = row.name.split(' ');
            return parts[0] || row.name;
        }).filter(Boolean);

        const text = `Приказ о премировании: за добросовестный труд премировать сотрудников — ${names.join(', ')}.`;
        if (this.bonusBlock) {
            this.bonusBlock.textContent = text;
            this.bonusBlock.classList.add('bonus-result--visible');
        }
    }

    _esc(str) {
        const d = document.createElement('div');
        d.textContent = str || '';
        return d.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('contacts-table-app');
    if (root) {
        new ContactsTable({ apiUrl: root.dataset.apiUrl });
    }
});
