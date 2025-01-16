import dash
from dash import Dash, html, dcc,Input, Output,State,callback
import dash_bootstrap_components as dbc
import logging,requests
from flask import jsonify

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)
app = Dash(__name__, use_pages=True,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dash.page_container
])


stored_data = [
    {"id": 1, "name": "Alice", "age": 25},
    {"id": 2, "name": "Bob", "age": 30},
    {"id": 3, "name": "Charlie", "age": 35}
]

# Define API endpoint to serve JSON data
@server.route('/data', methods=['GET'])
def serve_json_data():
    return jsonify(stored_data)

@server.route("/api", methods=["POST"])
def process_json():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        data["processed"] = True
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500