import os, json

# from .kot import Kotak_Neo_Login
from .FlatTradeTicker import Flat_Trade_Socket
from ..loginmgmt.session_manger import SessionManager
from ..Utils.Fields import F
from ..Utils.Path import Path
from ..Utils.Fields import F


class Ticker_Manger:
    Broker = None
    is_open = False

    @staticmethod
    def get():
        # SessionManager.
        login_cred = SessionManager.User_Config
        SessionManager.login_cred = login_cred
        # for i in login_cred:
        if login_cred[F.BROKER_NAME] == F.KOTAK_NEO:
            # SessionManager.User_Config[F.SESSION] = broker_session
            pass

        if login_cred[F.BROKER_NAME] == F.FLAT_TRADE:
            Ticker_Manger.Broker = Flat_Trade_Socket
            return Flat_Trade_Socket(SessionManager.User_Config[F.SESSION])
                
        # elif call other broker login method:
      