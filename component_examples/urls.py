"""URL configuration for component examples."""

from django.urls import path

from component_examples import views, views_data_star as ds_views

base_patterns = [
    path("alert/", views.alert_view, name="alert"),
    path("toast/", views.toast_view, name="toast"),
    path("table/", views.table_view, name="table"),
    path("tabs/", views.tabs_view, name="tabs"),
]

data_star_patterns = [
    # path("ds-alert/", views.ds_alert_view, name="ds_alert"),
    path(
        "ds-alert/",
        ds_views.show_alert,
        name="ds_show_alert",
    ),
    path(
        "ds-toast/",
        ds_views.show_toast,
        name="ds_show_toast",
    ),
    path(
        "ds-table/more/",
        ds_views.load_table_rows,
        name="ds_load_table_rows",
    ),
    path(
        "ds-table/sort/",
        ds_views.sort_table,
        name="ds_sort_table",
    ),
]

urlpatterns = base_patterns + data_star_patterns
