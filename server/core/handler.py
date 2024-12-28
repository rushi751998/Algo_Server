# from ..ordermgmt.kotak_neo import KotakManager
from ..ordermgmt.Flat_Trade import FlatTrade
from ..loginmgmt.session_manger import SessionManager
from ..Utils.Fields import F

class SessionHandler:
    broker = None
    def set_session():
        # if user[F.BROKER_NAME] == F.KOTAK_NEO:
        #     SessionHandler.broker = KotakManager
            
        if SessionManager.User_Config[F.BROKER_NAME] == F.FLAT_TRADE:
            SessionHandler.broker = FlatTrade