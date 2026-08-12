/**
 * Демонстрация дополнительных Web API (ЛР3, задание 9).
 */
document.addEventListener('DOMContentLoaded', () => {
    const geoBtn = document.getElementById('btn-geolocation');
    const geoOut = document.getElementById('geo-result');
    const speechBtn = document.getElementById('btn-speech');
    const speechText = document.getElementById('speech-text');
    const batteryOut = document.getElementById('battery-result');

    if (geoBtn && geoOut) {
        geoBtn.addEventListener('click', () => {
            if (!navigator.geolocation) {
                geoOut.textContent = 'Геолокация не поддерживается.';
                return;
            }
            geoOut.textContent = 'Определение координат…';
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    geoOut.textContent = `Широта: ${pos.coords.latitude.toFixed(5)}, долгота: ${pos.coords.longitude.toFixed(5)}`;
                },
                (err) => { geoOut.textContent = `Ошибка: ${err.message}`; }
            );
        });
    }

    if (speechBtn && speechText) {
        speechBtn.addEventListener('click', () => {
            if (!window.speechSynthesis) {
                alert('Speech Synthesis API недоступен.');
                return;
            }
            const utter = new SpeechSynthesisUtterance(speechText.value || 'Добро пожаловать в музей искусств!');
            utter.lang = 'ru-RU';
            utter.rate = 0.95;
            speechSynthesis.speak(utter);
        });
    }

    if (batteryOut) {
        if (navigator.getBattery) {
            navigator.getBattery().then((battery) => {
                const update = () => {
                    batteryOut.textContent = `Заряд: ${Math.round(battery.level * 100)}%, заряжается: ${battery.charging ? 'да' : 'нет'}`;
                };
                update();
                battery.addEventListener('levelchange', update);
                battery.addEventListener('chargingchange', update);
            }).catch(() => {
                batteryOut.textContent = 'Battery API недоступен.';
            });
        } else {
            batteryOut.textContent = 'Battery API не поддерживается в этом браузере.';
        }
    }
});
