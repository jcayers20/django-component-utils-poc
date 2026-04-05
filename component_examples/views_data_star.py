"""Views used for data-star integration examples."""

import secrets
from io import StringIO

import pandas as pd
from datastar_py.consts import ElementPatchMode
from datastar_py.django import (
    DatastarResponse,
    ServerSentEventGenerator,
    read_signals,
)
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.template.loader import render_to_string
from lorem_text import lorem

from utils.components import alert, toast


@login_required
def show_alert(request):
    signals = read_signals(request)
    variant = signals.get("variant", "primary")
    title = signals.get("title", "")
    icon = signals.get("icon", "")
    dismissible = signals.get("dismissible", False)
    auto_dismiss = signals.get("auto_dismiss", False)
    delay = float(signals.get("delay", 5.0))

    text = f"This is an alert with variant {variant}"
    footer = None
    if auto_dismiss:
        footer = f"This alert will disappear after {delay} seconds"

    # generate random CSS element ID for the alert to avoid conflicts
    css_id = secrets.token_hex(12)

    generated_alert = alert.create_alert(
        text=text,
        variant=variant,
        title=title,
        icon=icon,
        dismissible=dismissible,
        auto_dismiss=auto_dismiss,
        delay=delay,
        footer=footer,
        css_id=css_id,
    )

    response = ServerSentEventGenerator.patch_elements(
        generated_alert,
        selector="#alert-demo",
        mode=ElementPatchMode.APPEND,
    )
    return DatastarResponse(response)


@login_required
def show_toast(request):

    # determine toast params from signal values
    signals = read_signals(request)
    variant = signals.get("variant", "primary")
    title = signals.get("title", "")
    text = (signals.get("text", "") or "").strip() or lorem.words(50)
    icon = (signals.get("icon", "") or "").strip() or None
    dismissible = signals.get("dismissible", False)
    auto_dismiss = signals.get("auto_dismiss", False)
    delay = float(signals.get("delay", 5.0))

    # create the toast HTML using component function
    toast_to_send = toast.create_toast(
        text=text,
        css_id=f"toast-{variant or 'default'}",
        title=title,
        variant=variant,
        icon=icon,
        dismissible=dismissible,
        auto_dismiss=auto_dismiss,
        delay=delay,
    )

    # send the toast as an SSE patch
    response = ServerSentEventGenerator.patch_elements(
        toast_to_send,
        selector="#toast-container",
        mode=ElementPatchMode.APPEND,
    )
    return DatastarResponse(response)


@login_required
def load_table_rows_new(request):

    def handle_cache_miss() -> DatastarResponse:
        toast_message = (
            "No cached data found. Please refresh the page to load the data."
        )
        toast_html = toast.create_toast(
            text=toast_message,
            title="Error Loading Data",
            variant="danger",
            delay=10,
        )
        show_toast_event = ServerSentEventGenerator.patch_elements(
            toast_html,
            selector="#toast-container",
            mode=ElementPatchMode.APPEND,
        )
        response = DatastarResponse(show_toast_event)
        return response

    # get event signals
    signals = read_signals(request)

    # check whether target key exists in cache
    target = signals["target"]
    target_contents = cache.get(target)
    target_exists = target_contents is not None

    # if target key doesn't exist, handle the cache miss and we're done
    if not target_exists:
        return handle_cache_miss()

    # if target key exists, check whether it contains data
    if target_exists:
        target_is_valid = (
            isinstance(target_contents, dict) and "data" in target_contents
        )

    # if no data in target, handle the cache miss and we're done
    if not target_is_valid:
        return handle_cache_miss()

    # extract data into a DataFrame
    data = StringIO(pd.read_json(StringIO(target_contents["data"])))
    element_id = target_contents.get("element_id", "")

    # update page number state
    n_pages = int(target_contents.get("n_pages", 1)) + 1
    target_contents.update({"n_pages": str(n_pages)})

    # get the next page of data
    page_size = int(target_contents.get("page_size", 10))
    start_idx = n_pages * page_size
    end_idx = start_idx + page_size
    page_data = data.iloc[start_idx:end_idx]

    # create HTML for the page
    page_html = render_to_string(
        template_name="components/table/table_body.html",
        context={"data": page_data},
    )

    # create SSE to append the new rows to the table
    events = []
    append_rows_event = ServerSentEventGenerator.patch_elements(
        page_html,
        selector=f"#{element_id}-body",
        mode=ElementPatchMode.APPEND,
    )
    events.append(append_rows_event)

    # if no more pages of data to load, create SSE to remove the "Load More" element
    if end_idx >= len(data):
        remove_load_more_event = ServerSentEventGenerator.patch_elements(
            "",
            selector=f"#{element_id}-load-more",
            mode=ElementPatchMode.REMOVE,
        )
        events.append(remove_load_more_event)

    # combine events into a single response
    return DatastarResponse(events)


@login_required
def load_table_rows(request):

    # get event signals
    signals = read_signals(request)

    # get data from cache if it exists
    prefix = signals["prefix"]
    cache_key = signals.get(f"{prefix}_cache_key", "")
    cache_data = cache.get(cache_key)
    if cache_data is not None:
        data = pd.read_json(StringIO(cache_data), orient="records")
        data = data.drop(columns=["_original_index"])

    # if no cached data, show an alert indicating the issue and asking user to refresh the page
    else:
        toast_message = (
            "No cached data found. Please refresh the page to load the data."
        )
        toast_html = toast.create_toast(
            text=toast_message,
            title="Error Loading Data",
            variant="danger",
            delay=10,
        )
        show_toast_event = ServerSentEventGenerator.patch_elements(
            toast_html,
            selector="#toast-container",
            mode=ElementPatchMode.APPEND,
        )
        return DatastarResponse(show_toast_event)

    # get HTML table data for the next page
    page_number = int(signals.get(f"{prefix}_n_pages", 1))
    page_size = int(signals.get(f"{prefix}_page_size", 10))
    start_idx = page_number * page_size
    end_idx = start_idx + page_size
    page_data = data.iloc[start_idx:end_idx]
    page_html = render_to_string(
        template_name="components/table/table_body.html",
        context={"data": page_data},
    )

    # create SSE to append new rows to the table body
    events = []
    append_rows_event = ServerSentEventGenerator.patch_elements(
        page_html,
        selector=f"#{prefix}-body",
        mode=ElementPatchMode.APPEND,
    )
    events.append(append_rows_event)

    # create SSE to update the pagination info
    signal_patches = {
        f"{prefix}_n_pages": str(page_number + 1),
    }
    update_page_number_event = ServerSentEventGenerator.patch_signals(
        signal_patches,
    )
    events.append(update_page_number_event)

    # if no more pages of data to load, create SSE to remove the "Load More" element
    if end_idx >= len(data):
        remove_load_more_event = ServerSentEventGenerator.patch_elements(
            "",
            selector=f"#{prefix}-load-more",
            mode=ElementPatchMode.REMOVE,
        )
        events.append(remove_load_more_event)

    # combine events into a single response
    return DatastarResponse(events)


def sort_table(request):

    # get event signals
    signals = read_signals(request)

    # save signals as variables to improve downstream readability
    prefix = signals["prefix"]
    cache_key = signals.get(f"{prefix}_cache_key", "")
    sort_dict = signals.get(f"{prefix}_sort", {})
    if sort_dict == "":
        sort_dict = {}
    n_pages = int(signals.get(f"{prefix}_n_pages", 1))
    page_size = int(signals.get(f"{prefix}_page_size", -1))
    multi_sort = signals.get("is_ctrl_pressed", False)
    last_clicked_column = signals.get(f"{prefix}_last_sort", "")

    # get data from cache if it exists
    cache_data = cache.get(cache_key)
    if cache_data is not None:
        data = pd.read_json(StringIO(cache_data), orient="records")

    # if no cached data, show an alert indicating the issue and asking user to refresh the page
    else:
        toast_message = (
            "No cached data found. Please refresh the page to load the data."
        )
        toast_html = toast.create_toast(
            text=toast_message,
            title="Error Loading Data",
            variant="danger",
            delay=10,
        )
        show_toast_event = ServerSentEventGenerator.patch_elements(
            toast_html,
            selector="#toast-container",
            mode=ElementPatchMode.APPEND,
        )
        return DatastarResponse(show_toast_event)

    # determine how the column will be sorted
    direction_list = ["", "asc", "desc"]
    current_direction = sort_dict.get(last_clicked_column, "")
    current_direction_idx = direction_list.index(current_direction)
    new_direction_idx = (current_direction_idx + 1) % 3
    new_direction = direction_list[new_direction_idx]

    # update sort dictionary based on whether multi-sort is enabled
    if multi_sort:
        if new_direction == "":
            sort_dict.pop(last_clicked_column, None)
        else:
            sort_dict[last_clicked_column] = new_direction
    else:
        sort_dict = {}
        if new_direction != "":
            sort_dict[last_clicked_column] = new_direction
        else:
            sort_dict = ""
    sort_dict = sort_dict or ""

    # sort the data based on the updated sort dictionary
    if len(sort_dict) > 0:
        sort_columns = list(sort_dict.keys())
        sort_ascending = [
            True if sort_dict[col] == "asc" else False for col in sort_columns
        ]
        data = data.sort_values(
            by=sort_columns,
            ascending=sort_ascending,
            kind="mergesort",  # stable sort to maintain order of equal elements
        )

    # if no sorting, return to original data order
    else:
        data = data.sort_values(by="_original_index", kind="mergesort")

    # cache sorted data
    cache.set(
        cache_key,
        data.to_json(orient="records"),
        timeout=3600,
    )

    # remove original index column so it is not displayed
    data = data.drop(columns=["_original_index"])

    # get first n pages of sorted data
    start_idx = 0
    end_idx = (n_pages * page_size) if page_size > 0 else len(data)
    page_data = data.iloc[start_idx:end_idx]

    # replace table body with sorted data
    page_html = render_to_string(
        template_name="components/table/table_body.html",
        context={"data": page_data},
    )
    events = []
    update_table_event = ServerSentEventGenerator.patch_elements(
        page_html,
        selector=f"#{prefix}-body",
        mode=ElementPatchMode.INNER,
    )
    events.append(update_table_event)

    # TODO create SSE to update sort info if needed
    signal_patches = {
        f"{prefix}_sort": sort_dict,
    }
    update_sort_event = ServerSentEventGenerator.patch_signals(
        signal_patches,
    )
    events.append(update_sort_event)

    # combine events into a single response
    return DatastarResponse(events)
