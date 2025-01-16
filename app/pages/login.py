import dash
from dash import Dash, html, dcc,Input, Output,State,callback
import dash_bootstrap_components as dbc
import logging
dash.register_page(__name__, path_template='/login')

layout = html.Div([html.H1('login')])