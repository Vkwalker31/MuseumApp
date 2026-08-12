/**
 * Базовый класс игрушки — прототипное наследование (ЛР3, задание 8).
 */
function Toy(name, price) {
    this._name = name;
    this._price = price;
    this._items = [];
}

Toy.prototype.getName = function () { return this._name; };
Toy.prototype.setName = function (v) { this._name = v; };
Toy.prototype.getPrice = function () { return this._price; };
Toy.prototype.setPrice = function (v) { this._price = v; };

Toy.prototype.addFromForm = function (formEl) {
    const name = formEl.querySelector('[name="toy_name"]')?.value.trim();
    const price = parseFloat(formEl.querySelector('[name="toy_price"]')?.value);
    const minAgeRaw = formEl.querySelector('[name="toy_min_age"]')?.value;
    const maxAgeRaw = formEl.querySelector('[name="toy_max_age"]')?.value;

    if (window.validateToyInput) {
        const err = validateToyInput(name, price, minAgeRaw, maxAgeRaw);
        if (err) return false;
    }

    const minAge = minAgeRaw === '' ? 0 : parseInt(minAgeRaw, 10);
    const maxAge = maxAgeRaw === '' ? 99 : parseInt(maxAgeRaw, 10);
    this._items.push({ name, price, minAge, maxAge });
    return true;
};

Toy.prototype.renderAll = function (container) {
    container.innerHTML = this._items.map((t) =>
        `<li>${t.name} — ${t.price} руб., ${t.minAge}–${t.maxAge} лет</li>`
    ).join('');
};

Toy.prototype.renderResult = function (container) {
    container.textContent = 'Добавьте игрушки для анализа.';
};

function AgeToy(name, price, minAge, maxAge) {
    Toy.call(this, name, price);
    this._minAge = minAge;
    this._maxAge = maxAge;
}

AgeToy.prototype = Object.create(Toy.prototype);
AgeToy.prototype.constructor = AgeToy;

AgeToy.prototype.getMinAge = function () { return this._minAge; };
AgeToy.prototype.setMinAge = function (v) { this._minAge = v; };
AgeToy.prototype.getMaxAge = function () { return this._maxAge; };
AgeToy.prototype.setMaxAge = function (v) { this._maxAge = v; };

AgeToy.prototype.findNearMaxPrice = function () {
    if (!this._items.length) return [];
    const maxPrice = Math.max(...this._items.map((t) => t.price));
    return this._items.filter((t) => maxPrice - t.price <= 1);
};

AgeToy.prototype.renderResult = function (container) {
    const found = this.findNearMaxPrice();
    if (!found.length) {
        container.textContent = 'Нет данных.';
        return;
    }
    const names = found.map((t) => t.name).join(', ');
    container.textContent = `Наиболее дорогие игрушки (разница ≤ 1 руб.): ${names}`;
};
