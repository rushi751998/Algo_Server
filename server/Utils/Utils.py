import pymongo
import os, json, requests
from  datetime import datetime as dt,timedelta,time as time_
from dotenv import load_dotenv
from typing import Dict, List 
from bs4 import BeautifulSoup
import ast
import datetime
import time
import logging
from .Path import Path
from .Fields import F
from ..models.ProductType import ProductType
from server.loginmgmt.session_manger import SessionManager
import pandas as pd


def is_hoilyday() : 
    try : 
        url = "https://zerodha.com/marketintel/holiday-calendar/"
        response = requests.get(url)
        hoilyday_dict = {5 : 'Saturday',6 : 'Sunday'}
        date = str(dt.today().date())
        weekday = dt.strptime(date, "%Y-%m-%d").weekday()
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            holiday_table = soup.find('table')
            
            if holiday_table:
                for row in holiday_table.find_all('tr')[1:]:  #
                    columns = row.find_all('td')
                    date_fetched = columns[1].text.strip()
                    # print(f'soup : {date_fetched}')
                    
                    date_fetched = dt.strptime(date_fetched, "%d %b %Y").date()
                    holiday_name = columns[2].text.strip()
                    hoilyday_dict[str(date_fetched)] = holiday_name
                
                # send_message(message = f'hoilyday_dict : {hoilyday_dict}')
                if (date in hoilyday_dict) or (weekday in hoilyday_dict):
                    reason = hoilyday_dict[date] if date in hoilyday_dict else hoilyday_dict[weekday]
                    return True, reason
                else:
                    return False, None

            else:
                send_message(message = "Holiday table not found on the page.", emergency = True)
                return False, False
    except Exception as e :     
        send_message(message = "Failed to retrieve NSE holiday data. Status code: {e}", emergency = True)
        return False, False
        
def is_market_time():
    current_time = dt.today().time()
    start_time = time_(hour = 9, minute = 10, second = 0)
    end_time = time_(hour = 15, minute = 30, second = 0)
    if (current_time > start_time) and (current_time < end_time):
        return True
    else : 
        return False
 
def sleep_till_next_day():
    now= dt.now()
    tomorow_9am = (now + timedelta(days=1)).replace(hour = 9, minute = 16, second = 0)
    # tomorow_9am = (now + timedelta(days=0)).replace(hour=9,minute=43,second=0)
    total_seconds = (tomorow_9am-now).total_seconds()
    time.sleep(total_seconds)
       
def get_ist_now():
    return dt.now() + timedelta(0)

def wait_until_next_minute():
    now = dt.now()
    next_minute = (now + timedelta(minutes = 1)).replace(second = 0, microsecond = 0)
    sleep_time = (next_minute - now).total_seconds()
    return sleep_time

def set_stratagy_config():
    Env.load()
    Path.load()
    try : 
        db_df = pd.DataFrame(database()[Env.today].find())[F.STRATAGY].unique()
    except Exception as e:
        db_df = []
    FS = {}
    RB = {}
    BTST = {}
    STBT = {}
    # Path.load_path()
    
    folder_path = Path.config_Fixed_SL
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            stratagy = (filename.split('.')[0])
            with open(os.path.join(folder_path, filename), 'r') as f:
                data = json.load(f)
                data[F.ENTRY_TIME] = dt.strptime(f"{Env.today} {data[F.ENTRY_TIME]}","%Y-%m-%d %H:%M")
                data[F.EXIT_TIME] = dt.strptime(f"{Env.today} {data[F.EXIT_TIME]}","%Y-%m-%d %H:%M")
                data[F.ALLOWD] = bool(data[F.ALLOWD])
                
                if data[F.ALLOWD] :
                    if stratagy in db_df:
                        data[F.TRADED] = True
                    else :
                        data[F.TRADED] = False
                    
                    FS[stratagy]= data
                    logging.info(f'Loded {filename}')
                
                
    folder_path = Path.config_Range_Breakout
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            stratagy = (filename.split('.')[0])
            with open(os.path.join(folder_path, filename), 'r') as f:
                data = json.load(f)
                data[F.RANGE_START] = dt.strptime(f"{Env.today} {data[F.RANGE_START]}","%Y-%m-%d %H:%M")
                data[F.RANGE_END] = dt.strptime(f"{Env.today} {data[F.RANGE_END]}","%Y-%m-%d %H:%M")
                data[F.EXIT_TIME] = dt.strptime(f"{Env.today} {data[F.EXIT_TIME]}","%Y-%m-%d %H:%M")
                data[F.ALLOWD] = bool(data[F.ALLOWD])
                
                if data[F.ALLOWD] :
                    if stratagy in db_df:
                        data[F.TRADED] = True
                    else :
                        data[F.TRADED] = False
                        
                    RB[stratagy]= data
                    logging.info(f'Loded {filename}')
                    
    folder_path = Path.config_BTST
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            stratagy = (filename.split('.')[0])
            with open(os.path.join(folder_path, filename), 'r') as f:
                data = json.load(f)
                data[F.RANGE_START] = dt.strptime(f"{Env.today} {data[F.RANGE_START]}","%Y-%m-%d %H:%M")
                data[F.RANGE_END] = dt.strptime(f"{Env.today} {data[F.RANGE_END]}","%Y-%m-%d %H:%M")
                data[F.EXIT_TIME] = dt.strptime(f"{Env.today} {data[F.EXIT_TIME]}","%Y-%m-%d %H:%M")
                data[F.ALLOWD] = bool(data[F.ALLOWD])
                
                if data[F.ALLOWD] :
                    if stratagy in db_df:
                        data[F.TRADED] = True
                    else :
                        data[F.TRADED] = False
                        
                    BTST[stratagy]= data
                    logging.info(f'Loded {filename}')
                    
    folder_path = Path.config_STBT
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            stratagy = (filename.split('.')[0])
            with open(os.path.join(folder_path, filename), 'r') as f:
                data = json.load(f)
                data[F.ENTRY_TIME] = dt.strptime(f"{Env.today} {data[F.ENTRY_TIME]}","%Y-%m-%d %H:%M")
                data[F.EXIT_TIME] = dt.strptime(f"{Env.today} {data[F.EXIT_TIME]}","%Y-%m-%d %H:%M")
                data[F.ALLOWD] = bool(data[F.ALLOWD])
                
                if data[F.ALLOWD] :
                    if stratagy in db_df:
                        data[F.TRADED] = True
                    else :
                        data[F.TRADED] = False
                    
                    STBT[stratagy]= data
                    logging.info(f'Loded {filename}')
                
                
    Env.stratagy_config = {F.RANGE_BREAKOUT : RB,F.FIXED_SL:FS,F.STBT:STBT,F.BTST:BTST}

def time_tag():
   return str(round(time.time()))[-6:]

def setup_daily_logger(empty:bool = False):
    log_directory = 'log'
    os.makedirs(log_directory, exist_ok=True)
    today = str(dt.today().date())
    log_filename = os.path.join(log_directory, f'{today}.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s %(asctime)s %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Also print to console
        ]
    )
    # logging.info('Logger setup complete')
    # return logging

def is_straragy_traded(stratagy=None,traded_df=None,all_closed=False):
    if stratagy != None :
        traded_list = traded_df[F.stratagy].unique()
        return stratagy in traded_list
    if all_closed :
        if len(traded_df[traded_df[F.exit_orderid_status]==F.open]) > 0:
            return False
        else : 
            return True
                 
def database(day_tracker = False, recording = False):
    mongo_db = pymongo.MongoClient(Env.mongodb_link)
    if day_tracker :
        return mongo_db[f'Performance_{dt.now().year}']
    elif recording : 
        return mongo_db[F.recording]
    else : 
        return mongo_db[Env.database_name]
    
def send_message(message:str,user:dict,stratagy = None, emergency = False, send_image = False):
    current_time = dt.now()
    user = SessionManager.User_Config
    bot_chatId = SessionManager.User_Config['chatId']
    if not send_image : 
        if emergency : 
            bot_token = user['emergency_bot']
            # logging.warning(f'{message}\n')
            
        elif stratagy == None: 
            bot_token = user['common_logger']
            # logging.info(f'{message}\n')

        else : 
            bot_token = user[stratagy+"_bot"]
            # logging.info(f'{message}\n')
            
        message = f'{dt.strftime(current_time,"%H:%M:%S")}\n{message}'
        response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json = {'chat_id': bot_chatId,'text': message})
        if response.status_code != 200:
            message = f"{stratagy}_bot not able to send message Reason : {response.text}" 
            logging.warning(f'Retry Trigger_finder responce : {message}')
            bot_token = user['emergency_bot']
            message = f'{dt.strftime(current_time,"%H:%M:%S")}\n{message}'
            response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json = {'chat_id': bot_chatId,'text': message})
            logging.warning(f'Responce from retry : {response}')
            
            
    if send_image : 
        with open(message, 'rb') as file:
            bot_token = user['common_logger']
            url = url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            response = requests.post(url, data={'chat_id': bot_chatId}, files={'photo': file})
            if response.status_code != 200:
                message = ("Not able to send image")
                bot_token = user['emergency_bot']
                logging.warning(f'Retry Trigger_finder responce : {message}') 
                response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json = {'chat_id': bot_chatId,'text': message})
                logging.warning(f'Responce from retry-image : {response}')    
            
class Env:
    env_variable_initilised = False
    today = None
    thread_list = []
    stratagy_config = None
    socket_open = False
    LOT_SIZE = None
    DTE = None
    # option_chain : dict
    # logger = None #setup_daily_logger(True)
    selling_lots : int
    hedge_lots : int
    hedge_cost : float
    INDEX : str 
    expiry_base_instrument : bool
    product_type : str
    
    mongodb_link : str
    day_tracker : bool
    database_name : str

    capital : str
    qty_partation_loop : int
    telegram_api_dict : dict
    
    @classmethod
    def load (self):
        import os
        load_dotenv()
        setup_daily_logger()
        str_to_bool = {'False' : False,'True':True }
        self.hedge_cost = 0
        self.today = str(dt.now().date())
        self.expiry_base_instrument = str_to_bool[os.environ['expiry_base_instrument']]
        self.day_tracker = str_to_bool[os.environ['day_tracker']]
        
        self.mongodb_link = os.environ['mongodb_link'] 
        self.database_name = os.environ['database_name'] 
        
        self.product_type = ProductType.MIS
            
        self.allowed_loss_percent = float(os.environ['allowed_loss_percent'])
        self.qty_partation_loop = int(os.environ['qty_partation_loop'])
        # self.stratagy_config = set_stratagy_config()

        return True

 