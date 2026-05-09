"""Generic helpers for chart components."""

from copy import deepcopy
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
        self._validate_options()

    def _validate_options(self) -> None:
        if not isinstance(self.options, dict):
            raise TypeError("options must be a dict")

        if "plugins" in self.options and not isinstance(
            self.options["plugins"], dict
        ):
            raise TypeError("options['plugins'] must be a dict")

        if "scales" in self.options and not isinstance(
            self.options["scales"], dict
        ):
            raise TypeError("options['scales'] must be a dict")

    def to_dict(self) -> dict:
        """Convert a Chart instance to a dictionary for use in Chart.js."""
        options = deep_merge_dicts(
            {"responsive": True, "maintainAspectRatio": False},
            self.options,
        )

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
            options = deep_merge_dicts(options, {"plugins": title_config})

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
        options = deep_merge_dicts(options, {"plugins": legend_config})

        return {"options": options}

    def to_html(self) -> str:
        """Render the BarChart as an HTML string."""
        context = {"chart": self}
        return render_to_string("components/chart/chart.html", context)


def deep_merge_dicts(
    base: dict | None,
    updates: dict | None = None,
) -> dict:
    """Recursively merge updates into a base dictionary.

    Args:
        base (dict | None): The dictionary to be updated.
        updates (dict | None, optional): The updates to apply. Defaults to None.

    Returns:
        dict: The updated base dictionary
    """
    # short-circuit if base is None
    if base is None:
        return updates or {}

    # short-circuit if no updates provided
    if not updates:
        return deepcopy(base)

    result = deepcopy(base)

    # apply updates recursively
    for key, value in updates.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result
