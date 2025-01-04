
import dash_bootstrap_components as dbc


def layout():
    return dbc.Container(
    dbc.Alert("Hi There ", color="success"),
    className="p-5",
)

