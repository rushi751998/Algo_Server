
import dash_bootstrap_components as dbc


def layout():
    return dbc.Container(
    dbc.Alert("Hello Bootstrap!", color="success"),
    className="p-5",
)

