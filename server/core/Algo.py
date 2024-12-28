import time
from threading import Thread
import pandas as pd
from .handler import SessionHandler
from ..loginmgmt.session_manger import SessionManager
from ..Utils.Fields import F
from ..Utils.Utils import Env, set_stratagy_config
from ..stratagies.fixed_sl import Fixed_SL
from ..stratagies.range_breakout import Range_Breakout
from ..stratagies.base_stratagy import Base_Stratagy
from ..ticker.Ticker_Manger import Ticker_Manger



class ProgramKilled(Exception):
    pass

class Algo:
    
    @staticmethod
    def Start():
        set_stratagy_config()
        SessionManager.login_users()
        SessionHandler.set_session()
        
        try :
            while True :
                if not Env.socket_open:
                    broker_ticker = Ticker_Manger.get()
                    Thread(target=broker_ticker.start_socket).start()
                    # broker_ticker.start_socket()
                time.sleep(3)
                order_book = SessionHandler.broker.Order_book()
                db = pd.DataFrame(Base_Stratagy.db().find())
                Fixed_SL(config=Env.stratagy_config[F.FIXED_SL],order_book=order_book, db_orders=db).Process()
                # break
                
        except KeyboardInterrupt:
                logging.warning("Program killed: running cleanup code")
                sys.exit(0)
            
        # while True :
        #     print(2)
        #     time.sleep(2)
        #     # check current time is in market hours

        #     # find order for perticular user

        #     # get ordebook of that user
            
        #     # susbcrie stratagies and pass orderbook and db
            
        #     # run Stratagy

        #     pass