/**
 * Классы игрушек — синтаксис class/extends (ЛР3, задание 8).
 */
class ToyBase {
    constructor(name, price) {
        this._name = name;
        this._price = price;
        this._items = [];
    }

    getName() { return this._name; }
    setName(v) { this._name = v; }
    getPrice() { return this._price; }
    setPrice(v) { this._price = v; }

    addFromForm(formEl) {
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
    }

    renderAll(container) {
        container.innerHTML = this._items.map((t) =>
            `<li>${t.name} — ${t.price} руб., ${t.minAge}–${t.maxAge} лет</li>`
        ).join('');
    }

    renderResult(container) {
        container.textContent = 'Добавьте игрушки для анализа.';
    }
}

class AgeToyExtended extends ToyBase {
    constructor(name, price, minAge, maxAge) {
        super(name, price);
        this._minAge = minAge;
        this._maxAge = maxAge;
    }

    getMinAge() { return this._minAge; }
    setMinAge(v) { this._minAge = v; }
    getMaxAge() { return this._maxAge; }
    setMaxAge(v) { this._maxAge = v; }

    findNearMaxPrice() {
        if (!this._items.length) return [];
        const maxPrice = Math.max(...this._items.map((t) => t.price));
        return this._items.filter((t) => maxPrice - t.price <= 1);
    }

    renderResult(container) {
        const found = this.findNearMaxPrice();
        if (!found.length) {
            container.textContent = 'Нет данных.';
            return;
        }
        const names = found.map((t) => t.name).join(', ');
        container.textContent = `Наиболее дорогие игрушки (разница ≤ 1 руб.): ${names}`;
    }
}
