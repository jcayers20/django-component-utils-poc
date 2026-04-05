"""Utilities for creating tabs."""

from django.template.loader import render_to_string
from django.urls import reverse

from utils import string_generator


def create_tabs(
    content: dict[str, str],
    css_id: str = None,
    icons: dict[str, str] | str = None,
    orientation: str = "horizontal",
    style: str = "pills",
    lazy: bool = False,
    active_tab: str = None,
) -> str:
    """
    Create the HTML for a set of Bootstrap 5 tabs.

    Args:
        content:
            A dictionary mapping tab names to their HTML content.
        css_id:
            Optional ID for the tabs container. If not provided, a random ID
            will be generated.
        icons:
            Optional dictionary mapping tab names to Material Symbol icon names.
            If provided, each tab name in `icons` must also be a key in
            `content`.
        orientation:
            "horizontal" or "vertical" (or "h"/"v"). Defaults to "horizontal".
        style:
            "pills" or "tabs". Defaults to "pills".
        lazy:
            If True, tab content will only be rendered when the tab is selected.
            If True, then each tab's content must be a valid URL name (including
            namespace if applicable) and must return a `DatastarResponse`.
            Defaults to False.
        active_tab:
            The name of the tab that should be active by default. Defaults to
            the first tab.
    """
    # extract tab names and content
    tab_names = list(content.keys())
    if lazy:
        tab_content = [reverse(url_name) for url_name in content.values()]
    else:
        tab_content = list(content.values())

    # create a random CSS ID if none is provided
    if css_id is None:
        css_id = string_generator.generate_random_string()

    # create tab ID's
    tab_ids = [f"{css_id}-tab-{i}" for i in range(len(tab_names))]

    # process icon dictionary
    if not icons:
        icons = {tab_name: None for tab_name in tab_names}
    elif isinstance(icons, str):
        icons = {tab_name: icons for tab_name in tab_names}
    else:
        for tab_name, icon_name in icons.items():
            if tab_name not in tab_names:
                msg = f"Icon provided for tab '{tab_name}', but no content provided for that tab."
                raise ValueError(msg)

        icons = {tab_name: icons.get(tab_name) for tab_name in tab_names}
    tab_icons = list(icons.values())

    # validate orientation
    orientation = orientation.lower()
    horizontal_aliases = ["horizontal", "h"]
    vertical_aliases = ["vertical", "v"]
    if orientation in horizontal_aliases:
        orientation = "horizontal"
    elif orientation in vertical_aliases:
        orientation = "vertical"
    else:
        msg = f"Invalid orientation: {orientation}. Must be 'horizontal' or 'vertical'."
        raise ValueError(msg)

    # validate style
    style = style.lower()
    if style not in ["pills", "tabs"]:
        msg = f"Invalid style: {style}. Must be 'pills' or 'tabs'."
        raise ValueError(msg)

    # determine active tab
    if active_tab is None:
        active_tab = tab_names[0]
    elif active_tab not in tab_names:
        msg = f"Active tab '{active_tab}' not found in content keys."
        raise ValueError(msg)
    is_active = [tab_name == active_tab for tab_name in tab_names]

    # combine all information into a single list for use in template
    tab_data = list(zip(tab_names, tab_content, tab_ids, tab_icons, is_active))

    # create tab HTML using appropriate template
    context = {
        "tab_data": tab_data,
        "css_id": css_id,
        "style": style,
    }
    template_name = f"components/tabs/tabs_{orientation}"
    if lazy:
        template_name = f"{template_name}_lazy"
    template_name = f"{template_name}.html"

    return render_to_string(template_name, context)


# USAGE: uv run python -m utils.components.tabs
if __name__ == "__main__":
    import django
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    content = {
        "Tab 1": "<p>This is the content of Tab 1.</p>",
        "Tab 2": "<p>This is the content of Tab 2.</p>",
        "Tab 3": "<p>This is the content of Tab 3.</p>",
    }
    icons = {
        "Tab 1": "home",
        "Tab 2": "settings",
        "Tab 3": "info",
    }
    html = create_tabs(
        content,
        icons=icons,
        orientation="vertical",
        style="tabs",
    )
    print(html)
