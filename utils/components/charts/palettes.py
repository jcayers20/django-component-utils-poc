"""Custom color palettes to be used in charts."""

import seaborn as sns


custom_palettes = {"cat": ["#f3c911", "#007ba7", "#89F336", "#888888"]}


def resolve_palette_colors(
    palette_name: str, num_colors: int = 10
) -> list[str]:
    """Get a list of colors for a given palette name."""

    # validate input types
    if not isinstance(palette_name, str):
        raise TypeError("palette_name must be a string")
    if not isinstance(num_colors, int) or num_colors < 1:
        raise ValueError("num_colors must be a positive integer")

    # if palette name matches a custom palette, return those colors
    if palette_name in custom_palettes:
        return custom_palettes[palette_name][:num_colors]

    # if not found in custom palettes, try to get from seaborn
    try:
        return sns.color_palette(palette_name, n_colors=num_colors).as_hex()

    # if not a valid seaborn palette name, return empty list
    # in this case, Chart.js will use its default colors
    except ValueError:
        return []
