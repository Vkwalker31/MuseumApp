/**
 * Валидация и единый UI для задания 8 (игрушки).
 */
window.validateToyInput = function (name, price, minAgeRaw, maxAgeRaw) {
    const trimmed = (name || '').trim();
    if (!trimmed) {
        return 'Название не может быть пустым.';
    }
    const priceNum = parseFloat(price);
    if (isNaN(priceNum) || priceNum <= 0) {
        return 'Цена должна быть больше нуля.';
    }
    const minAge = minAgeRaw === '' || minAgeRaw == null ? 0 : parseInt(minAgeRaw, 10);
    const maxAge = maxAgeRaw === '' || maxAgeRaw == null ? 99 : parseInt(maxAgeRaw, 10);
    if (isNaN(minAge) || minAge < 0) {
        return 'Минимальный возраст: только от 0 и выше.';
    }
    if (isNaN(maxAge) || maxAge < 0) {
        return 'Максимальный возраст: только от 0 и выше.';
    }
    if (minAge > maxAge) {
        return 'Минимальный возраст не может быть больше максимального.';
    }
    return null;
};

const TOY_DEMO_DATA = [
    { name: 'Кукла', price: 1500, minAge: 3, maxAge: 8 },
    { name: 'Кубики', price: 800, minAge: 2, maxAge: 5 },
    { name: 'Мяч', price: 500, minAge: 1, maxAge: 10 },
    { name: 'Конструктор', price: 1501, minAge: 5, maxAge: 12 },
    { name: 'Пазл', price: 600, minAge: 4, maxAge: 9 },
];

function initToysUI() {
    const list = document.getElementById('toy-list');
    const result = document.getElementById('toy-result');
    const form = document.getElementById('toy-form');
    const errorEl = document.getElementById('toy-error');
    const modeLabel = document.getElementById('toy-mode-label');
    if (!list || !form) return;

    const protoCollection = new AgeToy('Коллекция', 0, 0, 12);
    protoCollection._items = TOY_DEMO_DATA.map((t) => ({ ...t }));

    const classCollection = new AgeToyExtended('Коллекция ES6', 0, 0, 12);
    classCollection._items = TOY_DEMO_DATA.map((t) => ({ ...t }));

    let activeMode = 'proto';

    function getCollection() {
        return activeMode === 'proto' ? protoCollection : classCollection;
    }

    function render() {
        const c = getCollection();
        c.renderAll(list);
        c.renderResult(result);
    }

    document.querySelectorAll('[data-toy-mode]').forEach((btn) => {
        btn.addEventListener('click', () => {
            activeMode = btn.dataset.toyMode;
            document.querySelectorAll('[data-toy-mode]').forEach((b) => {
                b.classList.toggle('task-btn--active', b === btn);
                b.classList.toggle('task-btn--outline', b !== btn);
            });
            if (modeLabel) {
                modeLabel.textContent = activeMode === 'proto'
                    ? 'Прототипное наследование'
                    : 'class / extends';
            }
            render();
        });
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = form.querySelector('[name="toy_name"]').value;
        const price = form.querySelector('[name="toy_price"]').value;
        const minAge = form.querySelector('[name="toy_min_age"]').value;
        const maxAge = form.querySelector('[name="toy_max_age"]').value;

        const err = validateToyInput(name, price, minAge, maxAge);
        if (err) {
            if (errorEl) errorEl.textContent = err;
            return;
        }
        if (errorEl) errorEl.textContent = '';

        const c = getCollection();
        if (c.addFromForm(form)) {
            form.reset();
            render();
        }
    });

    render();
}

document.addEventListener('DOMContentLoaded', initToysUI);
