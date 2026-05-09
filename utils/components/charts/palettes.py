"""Custom color palettes to be used in charts."""

import seaborn as sns


custom_palettes = {
    "cat": ["#f3c911", "#000000", "#89F336", "#888888"],
}


def resolve_palette_colors(
    palette_name: str,
    num_colors: int = 10,
    alpha: float = 1.0,
) -> list[str]:
    """Get a list of colors for a given palette name."""

    # validate input types
    if not isinstance(palette_name, str):
        raise TypeError("palette_name must be a string")
    if not isinstance(num_colors, int) or num_colors < 1:
        raise ValueError("num_colors must be a positive integer")

    # if palette name matches a custom palette, return those colors
    if palette_name in custom_palettes:
        hex_codes = custom_palettes[palette_name][:num_colors]
        return [hex_to_rgba(hex_code, alpha=alpha) for hex_code in hex_codes]

    # if not found in custom palettes, try to get from seaborn
    try:
        hex_codes = sns.color_palette(
            palette_name, n_colors=num_colors
        ).as_hex()
        return [hex_to_rgba(hex_code, alpha=alpha) for hex_code in hex_codes]

    # if not a valid seaborn palette name, return empty list
    # in this case, Chart.js will use its default colors
    except ValueError:
        return []


def hex_to_rgba(
    hex_color: str,
    alpha: float = 1.0,
) -> str:
    """Convert a hex color string to an RGBA string with the given alpha."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("hex_color must be in the format #RRGGBB")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore
    return f"rgba({r}, {g}, {b}, {alpha})"
