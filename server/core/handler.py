from server.trademgmt.kotak_neo import KotakManager
from server.utils import F

class SessionHandler:
    def get(user):
        if user[F.broker_name] == F.kotak_neo:
            return KotakManager