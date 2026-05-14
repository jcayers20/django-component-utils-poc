"""Utilities for creating waterfall charts using Chart.js."""

from pydantic.dataclasses import dataclass

from .generics import Chart, deep_merge_dicts
from .palettes import hex_to_rgba


@dataclass(kw_only=True)
class WaterfallChart(Chart):
    """Data model describing a Chart.js waterfall (floating bar) chart."""

    labels: list[str]
    values: list[int | float]
    base_color: str = "#888888"
    increase_color: str = "#4CAF50"
    decrease_color: str = "#F44336"

    def to_dict(self) -> dict:
        """Convert a WaterfallChart instance to a dictionary for use in Chart.js."""
        chart_config = super().to_dict()
        waterfall_config = {
            "options": {
                "scales": {
                    "x": {
                        "stacked": True,
                        "grid": {"display": False},
                    }
                },
                "plugins": {
                    "waterfall_chart_utils": {
                        "tooltip_label_callback": True,
                    }
                },
            }
        }
        chart_config = deep_merge_dicts(chart_config, waterfall_config)

        # validate that values contains at least 3 elements (start, at least one change, end)
        if len(self.values) < 3:
            raise ValueError(
                "values must contain at least 3 elements (start, at least one change, end)"
            )

        # build data structure matching format expected by Chart.js floating bar chart
        data = []
        colors = []
        total = 0
        n_elements = len(self.values)
        for i, value in enumerate(self.values):
            # first/last value is starting point so base is 0 and color is base_color
            if i == 0 or i == n_elements - 1:
                data.append([0, value])
                colors.append(hex_to_rgba(self.base_color, alpha=0.8))
                if i == 0:
                    total = value
            # intermediate values are changes so base is total so far and color
            # depends on whether value is positive (increase) or negative (decrease)
            else:
                color = (
                    self.increase_color if value >= 0 else self.decrease_color
                )
                data.append([total, total + value])
                colors.append(hex_to_rgba(color, alpha=0.8))
                total += value
        dataset = {
            "data": data,
            "backgroundColor": colors,
            "barPercentage": 0.95,
            "categoryPercentage": 1.0,
        }

        return deep_merge_dicts(
            chart_config,
            {
                "type": "bar",
                "data": {"labels": self.labels, "datasets": [dataset]},
            },
        )


def create_waterfall_chart(
    labels: list[str],
    values: list[int | float],
    base_color: str = "#888888",
    increase_color: str = "#4CAF50",
    decrease_color: str = "#F44336",
    title: str | None = None,
    palette: str = "deep",
    options: dict | None = None,
) -> WaterfallChart:
    """Helper function to create a WaterfallChart instance."""
    return WaterfallChart(
        labels=labels,
        values=values,
        base_color=base_color,
        increase_color=increase_color,
        decrease_color=decrease_color,
        title=title,
        show_legend=False,
        palette=palette,
        options=options,
    )
