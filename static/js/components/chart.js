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


function createWaterfallChartLabel(context) {
    const raw = context.raw;
    const dataIndex = typeof context.dataIndex === 'number' ? context.dataIndex : -1;
    const datasetLength =
        context.chart?.data?.datasets?.[context.datasetIndex ?? 0]?.data?.length ??
        0;
    const isBoundary =
        dataIndex === 0 || dataIndex === datasetLength - 1;

    if (Array.isArray(raw) && raw.length === 2) {
        const [start, end] = raw;
        if (isBoundary) {
            return `${end}`;
        }

        const diff = end - start;
        const arrow = diff > 0 ? '↑' : diff < 0 ? '↓' : '→';
        const sign = diff >= 0 ? '+' : '';
        return `${start} ${arrow} ${end} (${sign}${diff})`;
    }

    if (raw && typeof raw === 'object') {
        const yValue = raw.y ?? raw[1];
        const xValue = raw.x ?? raw[0];
        if (typeof yValue === 'number' && typeof xValue === 'number') {
            if (isBoundary) {
                return `${yValue}`;
            }

            const diff = yValue - xValue;
            const arrow = diff > 0 ? '↑' : diff < 0 ? '↓' : '→';
            const sign = diff >= 0 ? '+' : '';
            return `${xValue} ${arrow} ${yValue} (${sign}${diff})`;
        }
    }

    const parsed = context.parsed;
    if (parsed != null) {
        const numericValue =
            typeof parsed === 'object' ? parsed.y ?? parsed.x : parsed;
        return numericValue != null ? `${numericValue}` : '';
    }

    return '';
}


function _handleWaterfallChartConfig(chartData) {
    const waterfallConfig = chartData?.options?.plugins?.waterfall_chart_utils;
    if (!waterfallConfig) {
        return chartData;
    }

    chartData.options = chartData.options || {};
    chartData.options.plugins = chartData.options.plugins || {};
    chartData.options.plugins.tooltip =
        chartData.options.plugins.tooltip || {};
    chartData.options.plugins.tooltip.callbacks =
        chartData.options.plugins.tooltip.callbacks || {};

    chartData.options.plugins.tooltip.callbacks.label =
        createWaterfallChartLabel;

    return chartData;
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

    // waterfall chart - use custom tooltip label callback
    if (chartData?.options?.plugins?.waterfall_chart_utils) {
        console.log('Applying waterfall tooltip callback for chart:', chart.id);
        chartData = _handleWaterfallChartConfig(chartData);
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
