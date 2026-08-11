/**
 * Функции валидации URL и телефона (ЛР3, задание 3).
 */

/**
 * URL должен начинаться с http:// или https:// и заканчиваться на .php или .html
 * @param {string} url
 * @returns {boolean}
 */
function validateUrl(url) {
    if (!url || typeof url !== 'string') return false;
    const trimmed = url.trim();
    const pattern = /^https?:\/\/.+\.(php|html)$/i;
    return pattern.test(trimmed);
}

/**
 * Телефон: +375 или 8, код оператора в скобках или без, пробелы и дефисы
 * @param {string} phone
 * @returns {boolean}
 */
function validatePhone(phone) {
    if (!phone || typeof phone !== 'string') return false;
    const digits = phone.replace(/\D/g, '');
    if (digits.length === 11 && digits.startsWith('8')) {
        return /^8\d{10}$/.test(digits);
    }
    if (digits.length === 12 && digits.startsWith('375')) {
        return /^375\d{9}$/.test(digits);
    }
    return false;
}

window.validateUrl = validateUrl;
window.validatePhone = validatePhone;
