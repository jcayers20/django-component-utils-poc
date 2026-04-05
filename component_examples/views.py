from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pandas as pd

from utils.components import table

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
