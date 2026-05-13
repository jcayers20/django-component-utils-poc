"""Utilities for creating pie charts using Chart.js."""

from pydantic.dataclasses import dataclass

from .generics import Chart, deep_merge_dicts
from .palettes import resolve_palette_colors


@dataclass(kw_only=True)
class PieChart(Chart):
    """Data model describing a Chart.js pie chart."""

    labels: list[str]
    values: list

    def to_dict(self) -> dict:
        """Convert a PieChart instance to a dictionary for use in Chart.js."""
        options = super().to_dict()

        dataset = {
            "data": self.values,
            "backgroundColor": resolve_palette_colors(
                palette_name=self.palette,
                num_colors=len(self.values),
                alpha=1.0,
            ),
        }

        return deep_merge_dicts(
            options,
            {
                "type": "pie",
                "data": {"labels": self.labels, "datasets": [dataset]},
            },
        )


def create_pie_chart(
    labels: list[str],
    values: list,
    title: str | None = None,
    palette: str = "deep",
    options: dict | None = None,
) -> PieChart:
    """Helper function to create a PieChart instance."""
    return PieChart(
        labels=labels,
        values=values,
        title=title,
        palette=palette,
        options=options,
    )
