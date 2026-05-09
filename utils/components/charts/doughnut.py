"""Utilities for creating doughnut charts using Chart.js."""

from pydantic.dataclasses import dataclass

from .generics import Chart, deep_merge_dicts
from .palettes import resolve_palette_colors


@dataclass(kw_only=True)
class DoughnutChart(Chart):
    """Data model describing a Chart.js doughnut chart."""

    labels: list[str]
    data: list
    cutout_size: str | int = "50%"

    def to_dict(self) -> dict:
        """Convert a DoughnutChart instance to a dictionary for use in Chart.js."""
        options = super().to_dict()

        dataset = {
            "data": self.data,
            "backgroundColor": resolve_palette_colors(
                self.palette, len(self.data)
            ),
        }

        return deep_merge_dicts(
            options,
            {
                "type": "doughnut",
                "data": {"labels": self.labels, "datasets": [dataset]},
                "options": {"cutout": self.cutout_size},
            },
        )


def create_doughnut_chart(
    labels: list[str],
    data: list,
    cutout_size: str | int = "50%",
    title: str | None = None,
    palette: str = "deep",
    options: dict | None = None,
) -> DoughnutChart:
    """Helper function to create a DoughnutChart instance."""
    return DoughnutChart(
        labels=labels,
        data=data,
        cutout_size=cutout_size,
        title=title,
        palette=palette,
        options=options,
    )
