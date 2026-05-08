"""Utilities for creating bar charts using Chart.js."""

from typing import Literal

import pandas as pd
import seaborn as sns
from pydantic.dataclasses import dataclass


from .generics import Chart
from .palettes import palettes


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
class BarChart(Chart):
    """Data model describing a Chart.js bar chart."""

    labels: list[str]
    data: BarChartDataset | list[BarChartDataset]
    orientation: Literal["vertical", "horizontal"] = "vertical"

    def to_dict(self) -> dict:
        """Convert a BarChart instance to a dictionary for use in Chart.js."""

        result = super().to_dict()

        result.update({"type": "bar"})

        # get palette colors
        if self.palette in palettes:
            palette_colors = palettes[self.palette]
        else:
            try:
                palette_colors = sns.color_palette(
                    self.palette,
                    n_colors=10,
                ).as_hex()
            except ValueError:
                print(
                    f"Warning: Palette '{self.palette}' not found. Using default colors."
                )
                palette_colors = sns.color_palette("deep", n_colors=10).as_hex()
        # apply default colors from palette if not specified in datasets
        default_colors = palette_colors.copy() if palette_colors else []
        data_list = (
            [self.data] if isinstance(self.data, BarChartDataset) else self.data
        )
        for dataset in data_list:
            if dataset.backgroundColor is None:
                dataset.backgroundColor = (
                    default_colors.pop(0) if default_colors else None
                )

        # construct data dictionary for Chart.js
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
            options.update({"indexAxis": "y"})

        # stack bars by default if not already configured in options
        if "scales" not in options:
            options["scales"] = {"y": {"stacked": True}, "x": {"stacked": True}}
        else:
            options["scales"].update(
                {"y": {"stacked": True}, "x": {"stacked": True}}
            )

        result["options"].update(options)

        return result

    def from_dataframe() -> "BarChart":
        """Create a BarChart instance from a pandas DataFrame."""
        raise NotImplementedError("This method is not yet implemented.")


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
