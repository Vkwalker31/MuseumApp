/**
 * График arccos(x) — ряд и Math.acos (ЛР3, задание 10, вариант 9).
 * arccos(x) = π/2 - Σ (2n)! / (4^n (n!)^2 (2n+1)) * x^(2n+1)
 */
(function () {
    function factorial(n) {
        if (n <= 1) return 1;
        let r = 1;
        for (let i = 2; i <= n; i++) r *= i;
        return r;
    }

    function seriesTerm(x, n) {
        const num = factorial(2 * n);
        const den = Math.pow(4, n) * Math.pow(factorial(n), 2) * (2 * n + 1);
        return num / den * Math.pow(x, 2 * n + 1);
    }

    function arccosSeries(x, terms) {
        let sum = 0;
        for (let n = 0; n < terms; n++) {
            sum += seriesTerm(x, n);
        }
        return Math.PI / 2 - sum;
    }

    function computeTable(step, terms) {
        const rows = [];
        for (let x = -1; x <= 1.0001; x += step) {
            const xv = Math.round(x * 100) / 100;
            const fx = arccosSeries(xv, terms);
            const mathFx = Math.acos(Math.max(-1, Math.min(1, xv)));
            const eps = Math.abs(fx - mathFx);
            rows.push({ x: xv, n: terms, fx, mathFx, eps });
        }
        return rows;
    }

    let chartInstance = null;

    function renderTable(rows) {
        const tbody = document.getElementById('arccos-tbody');
        if (!tbody) return;
        tbody.innerHTML = rows.map((r) => `
            <tr>
                <td>${r.x.toFixed(2)}</td>
                <td>${r.n}</td>
                <td>${r.fx.toFixed(6)}</td>
                <td>${r.mathFx.toFixed(6)}</td>
                <td>${r.eps.toExponential(2)}</td>
            </tr>
        `).join('');
    }

    function renderChart(rows, animate) {
        const canvas = document.getElementById('arccos-chart');
        if (!canvas || typeof Chart === 'undefined') return;

        const labels = rows.map((r) => r.x.toFixed(2));
        const dataSeries = rows.map((r) => r.fx);
        const dataMath = rows.map((r) => r.mathFx);

        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(canvas, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'F(x) — ряд arccos',
                        data: dataSeries,
                        borderColor: '#c0392b',
                        backgroundColor: 'rgba(192, 57, 43, 0.1)',
                        tension: 0.3,
                        fill: false,
                    },
                    {
                        label: 'Math F(x) — Math.acos',
                        data: dataMath,
                        borderColor: '#2980b9',
                        backgroundColor: 'rgba(41, 128, 185, 0.1)',
                        tension: 0.3,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                animation: animate ? { duration: 2000 } : false,
                plugins: {
                    title: {
                        display: true,
                        text: 'arccos(x): ряд vs Math.acos(x), |x| ≤ 1',
                        font: { size: 16 },
                    },
                    legend: { display: true, position: 'top' },
                    annotation: undefined,
                },
                scales: {
                    x: {
                        title: { display: true, text: 'x' },
                    },
                    y: {
                        title: { display: true, text: 'F(x)' },
                        min: -0.1,
                        max: Math.PI + 0.1,
                    },
                },
            },
            plugins: [{
                id: 'customAnnotation',
                afterDraw(chart) {
                    const { ctx, chartArea } = chart;
                    ctx.save();
                    ctx.font = '12px sans-serif';
                    ctx.fillStyle = '#555';
                    ctx.fillText('π/2 ≈ ' + (Math.PI / 2).toFixed(4), chartArea.left + 10, chartArea.top + 20);
                    ctx.fillText('|x| ≤ 1', chartArea.right - 60, chartArea.top + 20);
                    ctx.restore();
                },
            }],
        });
    }

    function saveChart() {
        const canvas = document.getElementById('arccos-chart');
        if (!canvas) return;
        const link = document.createElement('a');
        link.download = 'arccos-chart.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    }

    document.addEventListener('DOMContentLoaded', () => {
        const btnCalc = document.getElementById('btn-arccos-calc');
        const btnSave = document.getElementById('btn-arccos-save');
        const termsInput = document.getElementById('arccos-terms');
        const stepInput = document.getElementById('arccos-step');

        function run(animate) {
            const terms = parseInt(termsInput?.value, 10) || 20;
            const step = parseFloat(stepInput?.value) || 0.1;
            const rows = computeTable(step, terms);
            renderTable(rows);
            renderChart(rows, animate);
        }

        btnCalc?.addEventListener('click', () => run(true));
        btnSave?.addEventListener('click', saveChart);

        run(true);
    });
})();
