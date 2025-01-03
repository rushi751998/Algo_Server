import os, json, logging

# from .kotak_neo import Kotak_Neo_Login
from .flat_trade import Flat_Trade_Login
from ..Utils.Fields import F
from ..Utils.Path import Path
from ..Utils.Fields import F


class SessionManager:
    User_Config = {}

    @staticmethod
    def login_users():
        SessionManager.load_credentials()
        login_cred = SessionManager.User_Config
        SessionManager.login_cred = login_cred
        # for i in login_cred:
        if login_cred[F.BROKER_NAME] == F.KOTAK_NEO:
            is_login, broker_session = Kotak_Neo_Login().login(login_cred)
            SessionManager.User_Config[F.SESSION] = broker_session

        if login_cred[F.BROKER_NAME] == F.FLAT_TRADE:
            is_login, broker_session = Flat_Trade_Login().login(login_cred)
            SessionManager.User_Config[F.SESSION] = broker_session
                
        # elif call other broker login method:
                
    @staticmethod                
    def get_session():
        return SessionManager.User_Config[F.SESSION]
    
    @staticmethod
    def get_broker_name():
        return SessionManager.User_Config[F.BROKER_NAME]
    
    @staticmethod
    def load_credentials():
        all_stratagies = [F.FS_FIRST,
                          F.FS_SECOND,
                          F.FS_THIRD,
                          F.FS_FOURTH,
                          F.FS_FIFTH,
                          F.RB_FIRST,
                          F.RB_SECOND,
                          F.RB_THIRD,
                          F.RB_FOURTH,
                          F.RB_FIFTH,
                          F.RB_SIXTH]
        
        folder_path = Path.config_Login
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                with open(os.path.join(folder_path, filename), 'r') as f:
                    data = json.load(f)
                    if data[F.ALLOWD] == 'True' :
                        for i in all_stratagies:
                            name = i+'_qty'
                            if name in data : 
                                qty_str = data[name]
                                qty_str_split = [int(i) for i in  qty_str.split('-')]
                                data[name] = qty_str_split
                                
                            SessionManager.User_Config = data
                            
        logging.info('loaded Credentials')