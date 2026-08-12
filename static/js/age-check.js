/**
 * Проверка даты рождения и возраста (ЛР3, задание 7).
 */
(function () {
    const DAYS = ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'];

    function checkBirthDate(dateStr) {
        const birth = new Date(dateStr);
        if (isNaN(birth.getTime())) return null;

        const today = new Date();
        let age = today.getFullYear() - birth.getFullYear();
        const m = today.getMonth() - birth.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age -= 1;

        const dayName = DAYS[birth.getDay()];
        return { age, dayName, isAdult: age >= 18 };
    }

    document.addEventListener('DOMContentLoaded', () => {
        const input = document.getElementById('birthdate-check');
        const btn = document.getElementById('btn-birthdate-check');
        const result = document.getElementById('birthdate-result');

        if (!input || !btn) return;

        btn.addEventListener('click', () => {
            const info = checkBirthDate(input.value);
            if (!info) {
                if (result) result.textContent = 'Введите корректную дату.';
                return;
            }

            if (info.isAdult) {
                const msg = `Вам ${info.age} лет. День недели вашего рождения: ${info.dayName}.`;
                if (result) result.textContent = msg;
            } else {
                alert('Для использования сайта необходимо разрешение родителей (вам нет 18 лет).');
                if (result) result.textContent = `Вам ${info.age} лет — требуется разрешение родителей.`;
            }
        });
    });
})();
