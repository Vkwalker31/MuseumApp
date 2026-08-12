/**
 * 3D-эффект объёма при наведении на карточки (ЛР3, задание 6).
 */
function initCard3D(root) {
    const scope = root || document;
    scope.querySelectorAll('.card-3d').forEach((card) => {
        if (card.dataset.card3dInit) return;
        card.dataset.card3dInit = '1';

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const cx = rect.width / 2;
            const cy = rect.height / 2;
            const rotateX = ((y - cy) / cy) * -8;
            const rotateY = ((x - cx) / cx) * 8;
            card.style.transform = `perspective(600px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.04, 1.04, 1.04)`;
            card.style.boxShadow = `${-rotateY}px ${rotateX + 10}px 30px rgba(0,0,0,0.25)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            card.style.boxShadow = '';
        });
    });
}

document.addEventListener('DOMContentLoaded', () => initCard3D());

window.initCard3D = initCard3D;
