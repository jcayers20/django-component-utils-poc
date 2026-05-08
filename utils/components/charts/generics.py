"""Generic helpers for chart components."""

from typing import Literal

from django.template.loader import render_to_string
from pydantic.dataclasses import dataclass

from utils.string_generator import generate_random_string


@dataclass(kw_only=True)
class Chart:
    css_id: str | None = None
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
        self.css_id = self.css_id or generate_random_string(length=12)
        self.script_id = f"{self.css_id}-data"

        self.options = self.options or {}

    def to_dict(self) -> dict:
        """Convert a Chart instance to a dictionary for use in Chart.js."""
        options = self.options.copy() if self.options else {}

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

        return {"options": options}

    def to_html(self) -> str:
        """Render the BarChart as an HTML string."""
        context = {"chart": self}
        return render_to_string("components/chart/chart.html", context)
