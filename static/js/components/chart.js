// function for handling chart download
function downloadChartImage(chartInstance, chartId) {
    let link = document.createElement('a');
    link.download = chartId + '.png';
    link.href = chartInstance.toBase64Image();
    link.click();
}


// for each element with class "chart-canvas", find the corresponding script tag with the chart data and render the chart
charts = document.querySelectorAll('.chart-canvas');
charts.forEach(chart => {
    console.log('Found chart canvas:', chart.id);
    let scriptId = chart.id + '-data';
    let chartData = JSON.parse(document.getElementById(scriptId).textContent);
    let ctx = chart.getContext('2d');
    let chartInstance =new Chart(ctx, chartData);

    // add event listener to download button
    let downloadButton = document.getElementById(chart.id + '-download');
    if (downloadButton) {
        downloadButton.onclick = () => {
            downloadChartImage(chartInstance, chart.id);
        };

    } else {
        alert('Download button not found for chart: ' + chart.id);
    }
});