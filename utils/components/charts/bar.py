"""Utilities for creating bar charts using Chart.js."""

from typing import Literal

import pandas as pd
from pydantic.dataclasses import dataclass


from .generics import Chart, deep_merge_dicts
from .palettes import resolve_palette_colors


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

    def __post_init__(self):
        super().__post_init__()

        if isinstance(self.data, BarChartDataset):
            self.data = [self.data]

        if not isinstance(self.data, list):
            raise TypeError(
                "data must be a BarChartDataset or a list of BarChartDataset instances"
            )

        if not self.labels:
            raise ValueError("labels must contain at least one value")

        if not self.data:
            raise ValueError("data must contain at least one dataset")

        for dataset in self.data:
            if len(dataset.data) != len(self.labels):
                raise ValueError(
                    "Each dataset length must match the number of labels"
                )

    def to_dict(self) -> dict:
        """Convert a BarChart instance to a dictionary for use in Chart.js."""

        result = super().to_dict()

        result.update({"type": "bar"})

        # get palette (default) colors
        num_colors = max(10, len(self.data))
        default_colors = resolve_palette_colors(
            self.palette,
            num_colors=num_colors,
        )

        # apply default colors from palette if not specified in datasets
        data_list = (
            [self.data] if isinstance(self.data, BarChartDataset) else self.data
        )
        datasets = []
        for dataset in data_list:
            # if dataset.backgroundColor is None:
            #     dataset.backgroundColor = (
            #         default_colors.pop(0) if default_colors else None
            #     )
            dataset_dict = dataset.to_dict()
            if dataset_dict.get("backgroundColor") is None:
                dataset_dict["backgroundColor"] = (
                    default_colors.pop(0) if default_colors else None
                )
            datasets.append(dataset_dict)

        # construct data dictionary for Chart.js
        data_dict = {
            "labels": self.labels,
            "datasets": datasets,
        }

        result["data"] = data_dict

        options = deep_merge_dicts(self.options, {})

        # apply horizontal orientation if specified
        if self.orientation == "horizontal":
            options = deep_merge_dicts(options, {"indexAxis": "y"})

        # stack bars by default if not already configured in options
        options = deep_merge_dicts(
            options,
            {"scales": {"y": {"stacked": True}, "x": {"stacked": True}}},
        )

        result["options"] = deep_merge_dicts(result["options"], options)

        return result


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
    elif not isinstance(value_col, list):
        raise TypeError("value_col must be a string or a list of strings")

    if value_labels is None:
        value_labels = value_col
    elif isinstance(value_labels, str):
        value_labels = [value_labels]
    elif not isinstance(value_labels, list):
        raise TypeError("value_labels must be a string or a list of strings")

    if len(value_labels) != len(value_col):
        raise ValueError("value_labels must have the same length as value_col")

    missing_columns = set([label_col] + value_col) - set(data.columns)
    if missing_columns:
        raise KeyError(f"Missing DataFrame columns: {sorted(missing_columns)}")

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
