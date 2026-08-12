/**
 * Генератор textarea с настройкой атрибутов (ЛР3, задание 4, вариант 9).
 * Сохранение в localStorage.
 */
class TextareaGenerator {
    constructor() {
        this.storageKey = 'museum-textareas';
        this.container = document.getElementById('generated-textareas');
        this.panel = document.getElementById('textarea-generator-panel');
        this.counter = 0;
        this._load();
        this._bind();
    }

    _bind() {
        document.getElementById('chk-add-textarea')?.addEventListener('change', (e) => {
            this.panel.hidden = !e.target.checked;
            if (e.target.checked && !this.container.children.length) {
                this.addTextarea();
            }
        });

        document.getElementById('btn-add-textarea')?.addEventListener('click', () => {
            this.addTextarea();
        });

        document.getElementById('btn-remove-textarea')?.addEventListener('click', () => {
            this.removeSelected();
        });
    }

    addTextarea(attrs = {}) {
        this.counter += 1;
        const id = `ta-${Date.now()}-${this.counter}`;
        const wrap = document.createElement('div');
        wrap.className = 'generated-textarea-wrap';
        wrap.dataset.id = id;

        const label = document.createElement('label');
        label.className = 'generated-textarea-label';
        label.innerHTML = `<input type="radio" name="textarea-select" value="${id}"> Textarea #${this.counter}`;

        const textarea = document.createElement('textarea');
        textarea.id = id;
        this._applyAttrs(textarea, attrs);

        const controls = document.createElement('div');
        controls.className = 'generated-textarea-controls';
        controls.innerHTML = this._controlsHTML(id, attrs);

        wrap.appendChild(label);
        wrap.appendChild(textarea);
        wrap.appendChild(controls);
        this.container.appendChild(wrap);

        controls.querySelectorAll('input, select').forEach((input) => {
            input.addEventListener('input', () => this._syncFromControls(id));
            input.addEventListener('change', () => this._syncFromControls(id));
        });

        this._save();
    }

    _controlsHTML(id, attrs) {
        return `
            <label>name <input type="text" data-attr="name" value="${attrs.name || ''}"></label>
            <label>rows <input type="number" data-attr="rows" min="1" value="${attrs.rows || 4}"></label>
            <label>cols <input type="number" data-attr="cols" min="1" value="${attrs.cols || 40}"></label>
            <label>placeholder <input type="text" data-attr="placeholder" value="${attrs.placeholder || ''}"></label>
            <label>maxlength <input type="number" data-attr="maxlength" min="1" value="${attrs.maxlength || 200}"></label>
            <label>wrap
                <select data-attr="wrap">
                    <option value="soft" ${attrs.wrap !== 'hard' ? 'selected' : ''}>soft</option>
                    <option value="hard" ${attrs.wrap === 'hard' ? 'selected' : ''}>hard</option>
                </select>
            </label>
            <label>readonly <input type="checkbox" data-attr="readonly" ${attrs.readonly ? 'checked' : ''}></label>
        `;
    }

    _applyAttrs(textarea, attrs) {
        if (attrs.name) textarea.name = attrs.name;
        if (attrs.rows) textarea.rows = attrs.rows;
        if (attrs.cols) textarea.cols = attrs.cols;
        if (attrs.placeholder) textarea.placeholder = attrs.placeholder;
        if (attrs.maxlength) textarea.maxLength = attrs.maxlength;
        textarea.wrap = attrs.wrap || 'soft';
        textarea.readOnly = !!attrs.readonly;
    }

    _syncFromControls(id) {
        const wrap = this.container.querySelector(`[data-id="${id}"]`);
        if (!wrap) return;
        const textarea = wrap.querySelector('textarea');
        const controls = wrap.querySelector('.generated-textarea-controls');

        const attrs = {};
        controls.querySelectorAll('[data-attr]').forEach((el) => {
            const key = el.dataset.attr;
            if (el.type === 'checkbox') attrs[key] = el.checked;
            else attrs[key] = el.value;
        });

        textarea.name = attrs.name || '';
        textarea.rows = parseInt(attrs.rows, 10) || 4;
        textarea.cols = parseInt(attrs.cols, 10) || 40;
        textarea.placeholder = attrs.placeholder || '';
        textarea.maxLength = parseInt(attrs.maxlength, 10) || 200;
        textarea.wrap = attrs.wrap || 'soft';
        textarea.readOnly = !!attrs.readonly;

        this._save();
    }

    removeSelected() {
        const selected = document.querySelector('input[name="textarea-select"]:checked');
        if (!selected) return;
        const wrap = this.container.querySelector(`[data-id="${selected.value}"]`);
        wrap?.remove();
        this._save();
    }

    _save() {
        const items = [];
        this.container.querySelectorAll('.generated-textarea-wrap').forEach((wrap) => {
            const textarea = wrap.querySelector('textarea');
            const controls = wrap.querySelector('.generated-textarea-controls');
            const attrs = { id: wrap.dataset.id };
            controls.querySelectorAll('[data-attr]').forEach((el) => {
                const key = el.dataset.attr;
                attrs[key] = el.type === 'checkbox' ? el.checked : el.value;
            });
            attrs.value = textarea.value;
            items.push(attrs);
        });
        localStorage.setItem(this.storageKey, JSON.stringify(items));
    }

    _load() {
        const raw = localStorage.getItem(this.storageKey);
        if (!raw) return;
        try {
            const items = JSON.parse(raw);
            items.forEach((item) => {
                this.addTextarea(item);
                const wrap = this.container.querySelector(`[data-id="${item.id}"]`);
                const textarea = wrap?.querySelector('textarea');
                if (textarea && item.value) textarea.value = item.value;
            });
            if (items.length) {
                document.getElementById('chk-add-textarea').checked = true;
                this.panel.hidden = false;
            }
        } catch (e) { /* ignore */ }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('generated-textareas')) {
        new TextareaGenerator();
    }
});
