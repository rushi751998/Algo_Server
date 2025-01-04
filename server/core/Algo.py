import time, logging
from threading import Thread
import pandas as pd
from .handler import SessionHandler
from ..loginmgmt.session_manger import SessionManager
from ..Utils.Fields import F
from ..Utils.Utils import Env, set_stratagy_config,is_market_time
from ..stratagies.fixed_sl import Fixed_SL
from ..stratagies.range_breakout import Range_Breakout
from ..stratagies.STBT import STBT
from ..stratagies.BTST import BTST
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
        
        while is_market_time() :
    
            if not Env.socket_open:
                broker_ticker = Ticker_Manger.get()
                Thread(target=broker_ticker.start_socket).start()
                time.sleep(5)
                # broker_ticker.start_socket()
            order_book = SessionHandler.broker.Order_book()
            db_orders = pd.DataFrame(Base_Stratagy.db().find())
            try :
                S1 = Thread(target = Fixed_SL(config=Env.stratagy_config[F.FIXED_SL],order_book=order_book, db_orders=db_orders).Process)
                # S2 = Thread(target = Range_Breakout(config=Env.stratagy_config[F.RANGE_BREAKOUT],order_book=order_book, db_orders=db).Process)
                # S3 = Thread(target = BTST(config=Env.stratagy_config[F.RANGE_BREAKOUT],order_book=order_book, db_orders=db).Process)
                # S4 = Thread(target = STBT(config=Env.stratagy_config[F.RANGE_BREAKOUT],order_book=order_book, db_orders=db).Process)
                
                S1.start()
                # S2.start()
                # S3.start()
                # S4.start()
                
                S1.join()
                # S2.join()
                # S3.join() 
                # S4.join()
                
                
            except KeyboardInterrupt:
                    logging.warning("Program killed: running cleanup code")
                    sys.exit(0)
                    
            except Exception as e :
                    logging.warning(f"Facing issue in Algo : {e}")
                    
            finally :
                time.sleep(2)
                
        # else :
        #     logging.WARNING("Market Stopped")