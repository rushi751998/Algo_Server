from .kotak_neo import Kotak_Neo_Login
from ..utils import F
import os, json

class SessionManager:
    sessions = {}
    login_cred_ = None

    @staticmethod
    def login_users():
        login_cred = SessionManager.load_credentials()
        SessionManager.login_cred = login_cred
        for i in login_cred:
            if login_cred[i][F.broker_name] == F.kotak_neo:
                # print(login_cred[i])
                is_login, broker_session = Kotak_Neo_Login().login(login_cred[i])
                SessionManager.sessions[i] = {F.BROKER_NAME : login_cred[i][F.broker_name], F.SESSION:broker_session}
                
    @staticmethod                
    def get_session(user):
        return SessionManager.sessions[user][F.SESSION]
    
    @staticmethod
    def get_broker_name(user):
        return SessionManager.load_cread_[user]['broker_name']
    
    @staticmethod
    def load_credentials():
        folder_path = 'D:/Pythoon/kotak_Server/config/login'
        login_cred = {}
        for filename in os.listdir(folder_path):
            # print(filename)
            if filename.endswith('.json'):
                with open(os.path.join(folder_path, filename), 'r') as f:
                    data = json.load(f)
                    if data['switch'] == 'True' :
                        # print(data)
                        login_cred[data['id']] = data
                        
        return login_cred
