// function for handling chart download
function downloadChartImage(chartInstance, chartId) {
    const link = document.createElement('a');
    link.download = `${chartId}.png`;
    link.href = chartInstance.toBase64Image();
    link.click();
}

function renderCharts() {
    const chartCanvases = document.querySelectorAll('.chart-canvas');

    chartCanvases.forEach((chart) => {
        console.log('Found chart canvas:', chart.id);

        const scriptElement = document.getElementById(`${chart.id}-data`);
        if (!scriptElement) {
            console.warn(`Data script not found for chart: ${chart.id}`);
            return;
        }

        let chartData;
        try {
            chartData = JSON.parse(scriptElement.textContent);
        } catch (error) {
            console.error(`Unable to parse chart data for ${chart.id}:`, error);
            return;
        }

        const ctx = chart.getContext('2d');
        if (!ctx) {
            console.warn(`Canvas context not available for chart: ${chart.id}`);
            return;
        }

        const chartInstance = new Chart(ctx, chartData);

        const downloadButton = document.getElementById(`${chart.id}-download`);
        if (downloadButton) {
            downloadButton.addEventListener('click', () => {
                downloadChartImage(chartInstance, chart.id);
            });
        } else {
            console.warn(`Download button not found for chart: ${chart.id}`);
        }
    });
}

document.addEventListener('DOMContentLoaded', renderCharts);
