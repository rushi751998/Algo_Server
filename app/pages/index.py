import dash
from dash import Dash, html, dcc,Input, Output,State,callback
import dash_bootstrap_components as dbc
import logging
dash.register_page(__name__, path_template='/')

layout = html.Div([
                    html.H1("Welcom To ABC Insurance")],id = 'index-main-div',className = 'index-main-div')

# @callback(
#         Output("login-button", "href"),
#         Input('login_email', 'value'),
#         Input('login_password', 'value'),   
#         [Input('login-button', 'n_clicks')]
#             )
# def login_page(login_email,login_password,n_clicks):
#     # print("--------------------124567")
#     email_id ='admin'   
#     password ='admin'
#     print(login_email,login_password)
#     # return None
#     if (login_email ==email_id) and (login_password==password) and (n_clicks!=None):
#         # print('\n',n_clicks)
#         return "/user_info"