// Resize Plotly graphs when their containing tab is shown
document.addEventListener("shown.bs.tab", function (event) {
  const targetSelector =
    event.target.getAttribute("href") || event.target.dataset.bsTarget;

  if (!targetSelector) {
    return;
  }

  const targetPane = document.querySelector(targetSelector);
  if (!targetPane) {
    return;
  }

  const plotlyGraphs = targetPane.querySelectorAll(".plotly-graph-div");
  plotlyGraphs.forEach(function (graphDiv) {
    if (window.Plotly && typeof Plotly.relayout === "function") {
      Plotly.relayout(graphDiv, { autosize: true });
    }
  });
});
