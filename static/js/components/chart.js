// for each element with class "chart-canvas", find the corresponding script tag with the chart data and render the chart
charts = document.querySelectorAll('.chart-canvas');
charts.forEach(chart => {
    console.log('Found chart canvas:', chart.id);
    let scriptId = chart.id + '-data';
    let chartData = JSON.parse(document.getElementById(scriptId).textContent);
    let ctx = chart.getContext('2d');
    new Chart(ctx, chartData);
});