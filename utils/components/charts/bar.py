"""Utilities for creating bar charts using Chart.js."""

from typing import Literal

import pandas as pd
import seaborn as sns
from django.template.loader import render_to_string
from pydantic.dataclasses import dataclass

accepted_palettes = [
    "bright",
    "colorblind",
    "dark",
    "deep",
    "muted",
    "pastel",
]
palettes = {
    palette: sns.color_palette(palette, n_colors=10).as_hex()
    for palette in accepted_palettes
}


@dataclass(kw_only=True)
class BarChartDataset:
    """Data model describing a dataset for a Chart.js bar chart."""

    label: str
    data: list
    backgroundColor: str = None
    borderColor: str | list[str] | None = None
    borderWidth: int | None = None

    def to_dict(self) -> dict:
        """Convert a BarChartData instance to a dictionary for use in Chart.js."""
        result = {
            "label": self.label,
            "data": self.data,
        }

        if self.backgroundColor:
            result["backgroundColor"] = self.backgroundColor
        if self.borderColor:
            result["borderColor"] = self.borderColor
        if self.borderWidth is not None:
            result["borderWidth"] = self.borderWidth

        return result


@dataclass(kw_only=True)
class BarChart:
    """Data model describing a Chart.js bar chart."""

    css_id: str | None = None
    labels: list[str]
    data: BarChartDataset | list[BarChartDataset]
    orientation: Literal["vertical", "horizontal"] = "vertical"
    title: str | None = None
    title_position: Literal["top", "left", "bottom", "right"] = "top"
    title_alignment: Literal["start", "center", "end"] = "center"
    show_legend: bool = True
    legend_position: Literal["top", "left", "bottom", "right"] = "bottom"
    legend_alignment: Literal["start", "center", "end"] = "center"
    palette: str = "deep"
    options: dict | None = None

    def __post_init__(self):
        """Hook to set default CSS ID's for chart and script elements."""
        if self.css_id is None:
            self.css_id = "chart"
        self.script_id = f"{self.css_id}-data"

        self.options = self.options or {}

    def to_dict(self) -> dict:
        """Convert a BarChart instance to a dictionary for use in Chart.js."""
        result = {
            "type": "bar",
        }

        default_colors = palettes.get(self.palette, []).copy()
        data_list = (
            [self.data] if isinstance(self.data, BarChartDataset) else self.data
        )
        for dataset in data_list:
            if dataset.backgroundColor is None:
                dataset.backgroundColor = (
                    default_colors.pop(0) if default_colors else None
                )

        data_dict = {
            "labels": self.labels,
            "datasets": [self.data.to_dict()]
            if isinstance(self.data, BarChartDataset)
            else [d.to_dict() for d in self.data],
        }
        result["data"] = data_dict

        options = self.options.copy() if self.options else {}

        # apply horizontal orientation if specified
        if self.orientation == "horizontal":
            options["indexAxis"] = "y"

        # configure chart title if provided
        if self.title:
            title_config = {
                "title": {
                    "display": True,
                    "text": self.title,
                    "position": self.title_position,
                    "align": self.title_alignment,
                }
            }
            if "plugins" in options:
                options["plugins"].update(title_config)
            else:
                options["plugins"] = title_config

        # configure legend display and position
        if not self.show_legend:
            legend_config = {"legend": {"display": False}}
        else:
            legend_config = {
                "legend": {
                    "display": True,
                    "position": self.legend_position,
                    "align": self.legend_alignment,
                }
            }
        if "plugins" in options:
            options["plugins"].update(legend_config)
        else:
            options["plugins"] = legend_config

        options["scales"] = {"y": {"stacked": True}, "x": {"stacked": True}}

        result["options"] = options

        return result

    def to_html(self) -> str:
        """Render the BarChart as an HTML string."""
        context = {"chart": self}
        return render_to_string("components/charts/bar.html", context)


def create_bar_chart(
    data: pd.DataFrame,
    label_col: str,
    value_col: str | list[str],
    css_id: str | None = None,
    value_labels: str | list[str] | None = None,
    orientation: Literal["vertical", "horizontal"] = "vertical",
    title: str | None = None,
    title_position: Literal["top", "left", "bottom", "right"] = "top",
    title_alignment: Literal["start", "center", "end"] = "center",
    show_legend: bool = True,
    legend_position: Literal["top", "left", "bottom", "right"] = "bottom",
    legend_alignment: Literal["start", "center", "end"] = "center",
    palette: str = "deep",
    options: dict | None = None,
) -> BarChart:
    """Create a BarChart instance from a pandas DataFrame."""
    if isinstance(value_col, str):
        value_col = [value_col]
    if value_labels is None:
        value_labels = value_col
    elif isinstance(value_labels, str):
        value_labels = [value_labels]

    datasets = []
    for col, label in zip(value_col, value_labels):
        dataset = BarChartDataset(
            label=label,
            data=data[col].tolist(),
        )
        datasets.append(dataset)

    return BarChart(
        css_id=css_id,
        labels=data[label_col].tolist(),
        data=datasets,
        orientation=orientation,
        title=title,
        title_position=title_position,
        title_alignment=title_alignment,
        show_legend=show_legend,
        legend_position=legend_position,
        legend_alignment=legend_alignment,
        palette=palette,
        options=options,
    )


if __name__ == "__main__":
    # Example usage
    df = pd.DataFrame(
        {
            "Month": ["January", "February", "March"],
            "Sales": [100, 150, 200],
            "Expenses": [80, 120, 160],
        }
    )

    chart = create_bar_chart(
        data=df,
        label_col="Month",
        value_col=["Sales", "Expenses"],
        value_labels=["Sales", "Expenses"],
        title="Monthly Sales and Expenses",
        title_position="top",
        title_alignment="start",
    )

    print(chart.to_dict())
    print(None or {})

    import seaborn as sns

    palette = sns.color_palette("bright", n_colors=10).as_hex()
    print(palette)
