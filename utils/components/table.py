"""Utilities for creating tables."""

import secrets
from io import StringIO

from django.core.cache import cache
from django.template.loader import render_to_string
import pandas as pd

from utils import string_generator
from utils.components import validation


def _get_cached_data(cache_key: str) -> pd.DataFrame:
    """
    Retrieve data from the cache if it exists.

    Args:
        cache_key (str): The key from which to retrieve cached data.

    Returns:
        pd.DataFrame: The cached data as a DataFrame.

    Raises:
        KeyError: If no data is found in the cache for the provided key.
    """
    cache_data = cache.get(cache_key).get("data")
    if cache_data is None:
        msg = f"No data found in cache for key {cache_key}."
        raise KeyError(msg)
    else:
        return pd.read_json(StringIO(cache_data), orient="records")


def create_table_new(
    data: pd.DataFrame = None,
    cache_key: str = None,
    on_conflict: str = "cache",
    cache_timeout: int = 3600,
    element_id: str = None,
    page_size: int = None,
    pagination_interface: str = "infinite_scroll",
) -> str:
    """
    Generate HTML to render an HTML table component.

    The table can be created from a provided DataFrame or from data stored in
    the cache. At least one of `data` or `cache_key` must be provided. If both
    are provided, the behavior depends on whether or not a key matching
    `cache_key` already exists in the cache and the value of `on_conflict`.
        - If no key matching `cache_key` exists, then `data` will be stored in
        the cache under `cache_key` and used to generate the table.
        - If a key matching `cache_key` already exists then the behavior depends
        on the value of `on_conflict`:
            - "cache": Use the cached data and ignore the provided data.
            - "overwrite": Overwrite the cached data with the provided data.
            - "error": Raise an error.

    The table supports the following features:
        - Sorting: Users can sort the table by clicking on column headers.
        Multi-column sorting is supported by holding down the CTRL key while
        clicking on multiple column headers.
        - Pagination: If `page_size` is provided, the table will display only
        `page_size` rows at a time and provide an interface for displaying more
        rows. The type of pagination interface is determined by
        `pagination_interface`. Supported options are "infinite_scroll" (more
        rows are loaded when the bottom of the table is reached) and
        "click_to_load" (user clicks a button to load more rows).

    Args:
        data (pd.DataFrame, optional):
            The data to be displayed in the table. Defaults to None.
        cache_key (str, optional):
            If `data` is provided, the key to which the data should be cached.
            If `data` is not provided, the key from which to retrieve cached
            data. Recommendation: make this key unique to the user who will see
            the table as table state will be shared by all users if not.
            Provided values must meet the following criteria:
                - First character must be a letter (a-z or A-Z).
                - Subsequent characters can be letters, digits (0-9),
                hyphens (-), or underscores (_).
        on_conflict (str, optional):
            What to do if `data` is provided and `cache_key` already exists in
            the cache. Defaults to "cache". Options:
                - "cache": Use the cached data and ignore the provided data.
                - "overwrite": Overwrite the cached data with the provided data.
                - "error": Raise an error.
        cache_timeout (int, optional):
            The timeout for the cache in seconds. Defaults to 3600 (1 hour).
        element_id (str, optional):
            The ID to assign to the <table> element. If not provided, then a
            random ID will be generated to ensure uniqueness. Provided values
            must meet the following criteria:
                - First character must be a letter (a-z or A-Z).
                - Subsequent characters can be letters, digits (0-9),
                hyphens (-), or underscores (_).
        page_size (int, optional):
            The number of rows to display per page. If not provided, then all
            rows will be displayed on a single page. Provided values must be
            greater than 0.
        pagination_interface (str, optional):
            The type of pagination interface to use if `page_size` is provided.
            Defaults to "infinite_scroll". Supported options are:
                - "infinite_scroll": More rows are loaded when the bottom of the
                table is reached.
                - "click_to_load": User clicks a button to load more rows.

    Returns:
        str: The HTML string to render the table.

    Raises:
        ValueError:
            - If neither `data` nor `cache_key` is provided.
            - If `on_conflict` is not one of "cache", "overwrite", or "error".
            - If `cache_timeout` is not a positive integer.
            - If `cache_key` or `element_id` do not meet the specified criteria.
            - If `page_size` is provided and is not greater than 0.
            - If `pagination_interface` is not one of "infinite_scroll" or
            "click_to_load".
            - If `on_conflict` is "error" and a key matching `cache_key` already
            exists in the cache.
        KeyError:
            - If an attempt is made to retrieve data from the cache but no data
            is found for the key.
    """

    # validate arguments
    valid_on_conflict_options = ["cache", "overwrite", "error"]
    if on_conflict not in valid_on_conflict_options:
        msg = f"Invalid value for on_conflict: {on_conflict}. Valid options are {valid_on_conflict_options}."
        raise ValueError(msg)
    if cache_timeout <= 0:
        msg = f"cache_timeout must be a positive integer, not {cache_timeout}."
        raise ValueError(msg)
    if cache_key is not None and not validation.validate_id(cache_key):
        msg = f"Invalid cache_key: {cache_key}. Key must start with a letter and can only contain letters, digits, hyphens, and underscores."
        raise ValueError(msg)
    if element_id is not None and not validation.validate_id(element_id):
        msg = f"Invalid element_id: {element_id}. ID must start with a letter and can only contain letters, digits, hyphens, and underscores."
        raise ValueError(msg)
    if page_size is not None and page_size <= 0:
        msg = f"If provided, page_size must be greater than 0, not {page_size}."
        raise ValueError(msg)
    valid_pagination_interfaces = ["infinite_scroll", "click_to_load"]
    if pagination_interface not in valid_pagination_interfaces:
        msg = f"Invalid pagination_interface: {pagination_interface}. Valid options are {valid_pagination_interfaces}."
        raise ValueError(msg)

    # generate random element ID if not provided
    element_id = element_id or string_generator.generate_random_string()

    # if no data or cache key provided, raise an error
    if data is None and cache_key is None:
        msg = "At least one of `data` or `cache_key` must be provided."
        raise ValueError(msg)

    # if cache key provided but no data, attempt to retrieve data from cache
    elif data is None and cache_key is not None:
        df = _get_cached_data(cache_key)

    # if data is provided, use it
    else:
        df = data.copy()
        if "_original_index" not in df.columns:
            df["_original_index"] = range(len(df))

        # get cache key, generating a random one if not provided
        cache_key = cache_key or string_generator.generate_random_string()

        # check whether cache key already exists in cache
        cache_key_data = cache.get(cache_key)

        # if cache key already exists, handle according to `on_conflict`
        if cache_key_data is not None:
            if on_conflict == "cache":
                data = pd.read_json(
                    StringIO(cache_key_data.get("data")),
                    orient="records",
                )
            elif on_conflict == "overwrite":
                cache_data = {
                    "data": df.to_json(orient="records"),
                }
                cache.set(cache_key, cache_data, timeout=cache_timeout)
            elif on_conflict == "error":
                msg = f"Cache key {cache_key} already exists in cache."
                raise ValueError(msg)

        # if cache key does not already exist, store data in cache
        else:
            cache_data = {
                "data": df.to_json(orient="records"),
            }
            cache.set(cache_key, cache_data, timeout=cache_timeout)

    # remove original index column if present
    if "_original_index" in df.columns:
        df = df.drop(columns=["_original_index"])

    # overwrite cached state data
    cache_data = {
        "element_id": element_id,
        "sort": {},
        "n_pages": 1,
        "page_size": page_size or -1,
    }
    cache[cache_key].update(cache_data)

    # create the table HTML
    context = {
        "data": df,
        "element_id": element_id,
        "cache_key": cache_key,
        "pagination_interface": pagination_interface,
    }
    return render_to_string(
        template_name="components/table/table_new.html",  # TODO create this
        context=context,
    )


def create_table(
    request,
    data: pd.DataFrame,
    css_id: str = None,
    page_size: int = None,
    pagination_interface: str = "infinite_scroll",
    cache_data: bool = True,
    cache_timeout: int = 3600,
    if_cache_exists: str = "use",
) -> str:
    """
    Render a Bootstrap 5 table component.

    Args:
        request (_type_): The request to the web server. Needed because data will be stored in the session.
        data (_type_): The data to be displayed in the table, typically a pandas DataFrame.
        css_id (str, optional): The CSS ID to assign to the table for styling purposes. If not provided a random one will be generated. Defaults to None.
        page_size (int, optional): The number of rows to display per page. If provided, must be greater than 0. Defaults to None (no pagination).t
        cache_data (bool, optional): Whether to cache the data in the session. Defaults to True.
        cache_timeout (int, optional): The timeout for the cache in seconds. Defaults to 3600 (1 hour).
        if_cache_exists (str, optional): What to do if cache already exists. Options are "use" to use the cached data or "overwrite" to overwrite the cache. Defaults to "use".

    Returns:
        str: The rendered HTML string.
    """
    df = data.copy()

    # store the data in the session so it can be accessed by the template
    if css_id is None:
        css_id = secrets.token_hex(24)
    cache_key = f"{css_id}_{request.user.pk}"

    # add original index as a column so it can be used for sorting
    df["_original_index"] = range(len(df))

    # use data from cache if we want to; otherwise store new data in the cache
    if if_cache_exists == "use":
        cache_data = cache.get(cache_key)
        if cache_data is not None:
            print("Using cached data.")
            df = pd.read_json(StringIO(cache_data), orient="records")
        else:
            print("No cached data found. Caching new data.")
            cache.set(
                cache_key,
                df.to_json(orient="records"),
                timeout=cache_timeout,
            )
    else:
        cache.set(
            cache_key,
            df.to_json(orient="records"),
            timeout=cache_timeout,
        )

    # remove original index column since it won't be displayed
    df = df.drop(columns=["_original_index"])

    if page_size is not None and page_size <= 0:
        msg = f"If provided, page_size must be greater than 0, not {page_size}"
        raise ValueError(msg)
    elif page_size is not None:
        df = df.iloc[:page_size]

    context = {
        "css_id": css_id,
        "cache_key": cache_key,
        "data": df,
        "page_size": page_size or -1,
        "pagination_interface": pagination_interface,
    }
    return render_to_string(
        template_name="components/table/table.html",
        context=context,
    )
