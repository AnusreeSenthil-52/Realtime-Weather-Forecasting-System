document.addEventListener('DOMContentLoaded', () => {

    const chartElement = document.getElementById('chart');
    if (!chartElement) {
        console.error('Canvas element not found');
        return;
    }

    const ctx = chartElement.getContext('2d');

    // Gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(250, 0, 0, 1)');
    gradient.addColorStop(1, 'rgba(136, 255, 0, 1)');

    // Forecast items
    const forecastItems = document.querySelectorAll('.forecast-item');

    const times = [];
    const temps = [];

    forecastItems.forEach(item => {
        const timeEl = item.querySelector('.forecast-time');
        const tempEl = item.querySelector('.forecast-temperatureValue');

        if (!timeEl || !tempEl) return;

        const time = timeEl.textContent.trim();
        const temp = parseFloat(
            tempEl.textContent.replace('°', '')
        );

        if (!isNaN(temp)) {
            times.push(time);
            temps.push(temp);
        }
    });

    if (times.length === 0 || temps.length === 0) {
        console.error('No forecast data found for chart');
        return;
    }

    // Chart.js
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: times,
            datasets: [{
                label: 'Temperature (°C)',
                data: temps,
                borderColor: gradient,
                borderWidth: 2,
                tension: 0.4,
                pointRadius: 3,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                }
            },
            scales: {
                x: {
                    display: false,
                    grid: {
                        drawOnChartArea: false,
                    }
                },
                y: {
                    display: false,
                    grid: {
                        drawOnChartArea: false,
                    }
                }
            },
            animation: {
                duration: 750,
            }
        }
    });
});
