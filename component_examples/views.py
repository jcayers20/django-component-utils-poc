from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pandas as pd
import plotly.express as px

from utils.components import alert, table, tabs

# Create your views here.


@login_required
def alert_view(request):
    return render(request, "show_alerts.html")


@login_required
def toast_view(request):
    return render(request, "show_toasts.html")


@login_required
def table_view(request):

    # create dataset large enough to demonstrate pagination and sorting
    data = pd.DataFrame(
        {
            "col1": range(1, 27),
            "col2": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        }
    )
    full_data = pd.concat(
        [data] * 1000, ignore_index=True
    )  # create more rows for pagination example
    full_data["col1"] = full_data.index + 1

    # create two tables with different pagination interfaces
    table_1_html = table.create_table(
        request=request,
        data=full_data,
        css_id="examplectl",
        page_size=26,
        pagination_interface="click_to_load",
    )
    table_2_html = table.create_table(
        request,
        data=full_data,
        css_id="exampleis",
        page_size=26,
        pagination_interface="infinite_scroll",
    )

    # render the tables in the template
    context = {
        "table_1_html": table_1_html,
        "table_2_html": table_2_html,
    }
    return render(
        request=request,
        template_name="show_table.html",
        context=context,
    )


def tabs_view(request):

    # create table to populate tab 1
    data = pd.DataFrame(
        {
            "col1": range(1, 27),
            "col2": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        }
    )
    full_data = pd.concat(
        [data] * 10, ignore_index=True
    )  # create more rows for pagination example
    full_data["col1"] = full_data.index + 1
    tab_1_html = table.create_table(
        request=request,
        data=full_data,
        css_id="tabs-table",
        page_size=26,
        pagination_interface="click_to_load",
    )

    # create alert to populate tab 2
    tab_2_html = alert.create_alert(
        text="Looks like the tabs are working!",
        css_id="tabs-alert",
        variant="success",
        title="All Systems Go",
        dismissible=True,
        # auto_dismiss=True,
        # delay=5,
    )

    # create a bar chart to populate tab 3
    data = pd.DataFrame(
        {
            "Category": ["A", "B", "C", "D", "E"],
            "Value": [10, 15, 7, 12, 20],
        }
    )
    chart = px.bar(data, x="Category", y="Value", title="Example Chart")
    tab_3_html = chart.to_html(include_plotlyjs="cdn", full_html=False)

    # create tabs
    content = {
        "Tab 1": tab_1_html,
        "Tab 2": tab_2_html,
        "Tab 3": tab_3_html,
    }
    icons = {
        "Tab 1": "hot_tub",
        "Tab 2": "timer",
        "Tab 3": "manufacturing",
    }
    tabs_html = tabs.create_tabs(
        content,
        icons=icons,
        orientation="horizontal",
        style="pills",
    )
    context = {"tabs_html": tabs_html}
    return render(request, "show_tabs.html", context)
