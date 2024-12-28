
import time, threading,logging
from ..Utils.Ticker_Selection import option_chain, token_to_ticker, option_type, ticker_to_token
from ..Utils.Path import Path
from ..Utils.Fields import F
from ..Utils.Utils import Env

from datetime import datetime as dt
import pandas as pd



class ProgramKilled(Exception):
    pass

class Flat_Trade_Socket:
    future_ticker : str
    tokens = []
    client = None
    
    def __init__(self,broker_session):
        self._lock = threading.Lock()  
        self.session = broker_session
        self.is_prepared = False
    
    def start_socket(self):
        if not self.is_prepared : 
            try : 
                future_ticker,is_prepared = self.prepare_option_chain_Future_token()
                # print(future_ticker)
                with self._lock:
                    self.future_ticker = future_ticker
                    self.is_prepared = is_prepared
            except Exception as e :
                print(e)
                # send_message(message = f'Facing Issue in prepare_option_chain_Future_token \nissue : {e}', emergency = True)

        if self.is_prepared : 
            # print(self.is_prepared)
            # token_list = [{"instrument_token":i,"exchange_segment":'nse_fo'} for i in option_chain.keys()]
            try :
                self.session.start_websocket(order_update_callback=self.on_order, subscribe_callback=self.update_option_chain, socket_open_callback=self.on_open,socket_close_callback = self.on_close,socket_error_callback = self.on_error)
                # self.session.subscribe(['NFO|46125'])
                self.session.subscribe(self.tokens)
    
                while True:
                    if Env.socket_open == True:
                        # time.sleep(1)
                        # # print(option_chain['NIFTY26DEC24C24500'])
                        # print(option_chain)
                        # print(5*'\n')
                        
                        pass

                    else:
                        continue

            except ProgramKilled:
                logging.warning("Program killed: running cleanup code")
                
            except Exception as e:
                print(e)
                # send_message(message = f'Facing Issue in Socket.start \nissue : {e}', emergency = True)
       
    def on_order(self,message):
        # logging.info(f'on_order : {message}')
        pass
                
    def on_open(self):
        logging.info(f'Socket_open')
        Env.socket_open= True
        # send_message(message = f'Socket Started : {message}')
        
    def on_close(self,message):
        Env.socket_open= False
        logging.warning(f'on_close : {message}')
        # send_message(message = f'Socket Started : {message}')
        
    def on_error(self,message):
        Env.socket_open= False
        logging.warning(f'on_error : {message}')
        # send_message(message = f'Socket Started : {message}')
               
    def update_option_chain(self, message):
        # print(message)
        
        try:
            token = message['tk']
            with self._lock:
                option_chain[token_to_ticker[token]][F.V] = int(message['v'])
        except:
            pass

        try:
            token = message['tk']
            with self._lock:
                option_chain[token_to_ticker[token]][F.OI] = int(tick['oi'])
        except:
            pass

        try:
            token = message['tk']
            with self._lock:
                # print(f'{token}  { float(message["lp"])}')
                option_chain[token_to_ticker[token]][F.LTP] = float(message['lp'])
                # print(option_chain[token_to_ticker[token]])
        except:
            pass

    def prepare_option_chain_Future_token(self):
        nse_fo = pd.read_csv(Path.config_Scripts+'flat_nse_fo.csv')
        bse_fo = pd.read_csv(Path.config_Scripts+'flat_bse_fo.csv')
        # bse_fo = pd.DataFrame()
        df = pd.concat([nse_fo,bse_fo])
        # df = df[df['Symbol'].isin(['NIFTY','SENSEX'])]
        df = df[df['Symbol'].isin(['NIFTY'])]

        df['DTE'] = df['Expiry'].apply(lambda x:(dt.strptime(str(x),'%d-%b-%Y').date()-dt.today().date()).days)
        df = df[df['DTE']>=0]
        df.sort_values('DTE',inplace=True)
        df.reset_index(inplace=True)

        option_df = df[df['DTE']==df['DTE'].min()]
        index = option_df.iloc[0]['Symbol']

        future_df = df[(df['Symbol'] == index) & (df['Optiontype'] == 'XX')]
        future_df = future_df[future_df['DTE']==future_df['DTE'].min()]
        future_ticker = future_df.iloc[0]['Tradingsymbol']

        Env.INDEX = index
        Env.LOT_SIZE = lot_size = int(option_df.iloc[0]['Lotsize'])
        Env.DTE = int(option_df.iloc[0]['DTE'])

        df = pd.concat([option_df,future_df])
        df.reset_index(inplace=True,drop=True)

        for index,row in df.iterrows():
                option_chain[row['Tradingsymbol']]  = {F.V:0, F.LTP:0 ,F.OI:0,F.OPTION_TYPE:row['Optiontype']}
                # token_to_ticker[str(row['Tradingsymbol'])] = row['Token']
                token_to_ticker[str(row['Token'])] = row['Tradingsymbol']
                ticker_to_token[str(row['Tradingsymbol'])] = row['Token']
                option_type[str(row['Tradingsymbol'])] = row['Optiontype']
                
                if row['Symbol'] == 'NIFTY':
                        self.tokens.append(f"NFO|{row['Token']}")
                        
                        
                elif row['Symbol'] == 'SENSEX':
                        self.tokens.append(f"BFO|{row['Token']}")

        logging.info('Prepared Option Chain')
        #  send_message(message = f'prepared opetion chain\nTodays instrument : {Env.index}')/
        return future_ticker,True
