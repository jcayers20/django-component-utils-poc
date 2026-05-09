// function for handling chart download
function downloadChartImage(chartInstance, chartId) {
    const link = document.createElement('a');
    link.download = `${chartId}.png`;
    link.href = chartInstance.toBase64Image();
    link.click();
}


function _handleSpecialBarChartConfig(chartData) {
    const barChartUtilsConfig = chartData?.options?.plugins?.bar_chart_utils;
    if (barChartUtilsConfig?.barmode === 'relative') {
        const valueAxis =
            barChartUtilsConfig.orientation === 'horizontal' ? 'x' : 'y';

        chartData.options = chartData.options || {};
        chartData.options.scales = chartData.options.scales || {};
        chartData.options.scales[valueAxis] =
            chartData.options.scales[valueAxis] || {};
        chartData.options.scales[valueAxis].ticks =
            chartData.options.scales[valueAxis].ticks || {};

        chartData.options.scales[valueAxis].ticks.callback = (value) =>
            `${Number(value).toFixed(0)}%`;

        chartData.options.plugins = chartData.options.plugins || {};
        chartData.options.plugins.tooltip =
            chartData.options.plugins.tooltip || {};
        chartData.options.plugins.tooltip.callbacks =
            chartData.options.plugins.tooltip.callbacks || {};

        chartData.options.plugins.tooltip.callbacks.label = (context) => {
            const datasetLabel = context.dataset?.label
                ? `${context.dataset.label}: `
                : '';
            const numericValue = Number(
                typeof context.parsed === 'object'
                    ? context.parsed[valueAxis]
                    : context.parsed
            );
            return `${datasetLabel}${numericValue.toFixed(2)}%`;
        };

        return chartData;
    } else {
        return chartData;
    }
}


function renderChart(chart) {
    console.log('Rendering chart:', chart.id);

    // get script element containing chart data
    const scriptElement = document.getElementById(`${chart.id}-data`);
    if (!scriptElement) {
        console.warn(`Data script not found for chart: ${chart.id}`);
        return;
    }

    // parse chart data
    let chartData;
    try {
        chartData = JSON.parse(scriptElement.textContent);
    } catch (error) {
        console.error(`Unable to parse chart data for ${chart.id}:`, error);
        return;
    }

    // get chart context
    const ctx = chart.getContext('2d');
    if (!ctx) {
        console.warn(`Canvas context not available for chart: ${chart.id}`);
        return;
    }

    // handle custom chart configuration based on chart type
    // bar chart - handle relative mode
    if (chart.type === 'bar') {
        console.log('Applying special bar chart configuration for chart:', chart.id);
        chartData = _handleSpecialBarChartConfig(chartData);
    }

    const chartInstance = new Chart(ctx, chartData);

    console.log('Finished rendering chart:', chart.id);

    return chartInstance;
}


function renderCharts() {
    const chartCanvases = document.querySelectorAll('.chart-canvas');

    chartCanvases.forEach((chart) => {
        console.log('Found chart canvas:', chart.id);

        const chartInstance = renderChart(chart);

        // enable image download functionality
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
