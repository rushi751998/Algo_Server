from server.core.Algo import Algo
from server.Utils.Utils import Env
from app.app import layout
from threading import Thread
import dash
import dash_bootstrap_components as dbc
import logging

Env.load()

logging.getLogger('werkzeug').disabled = True
logging.getLogger('dash').disabled = True

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = layout
    
def prod_run():
    app.run_server(debug = False)
    
def qa_run():
    app.run_server(debug = True)


if __name__ == '__main__':
    
    if Env.environment == 'prod':
        Thread(name='Algo_Server',target=Algo.Start).start()
        Thread(name='Dash_Server',target=prod_run).start()

    elif Env.environment == 'qa':
        # Thread(name='Algo_Server',target=Algo.Start).start()
        # Thread(name='Dash_Server',target=qa_run).start()
        qa_run()
    
    # Algo.Start()
    