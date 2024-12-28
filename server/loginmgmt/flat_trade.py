import requests,pyotp, time, logging
from datetime import datetime as dt
import hashlib
from threading import Timer
import pandas as pd
import concurrent.futures
from NorenRestApiPy.NorenApi import  NorenApi

from urllib.parse import parse_qs, urlparse
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


from .BaseLogin import BaseLogin
# from ..Utils.Utils import send_message
from ..Utils.Fields import F
from ..Utils.Path import Path


chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent /dev/shm issues
chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging port

option_chain = {}
token_to_ticker= {}
nan = 'nan'




class FlatTradeAPI(NorenApi):
    def __init__(self,userid,password,token):
        # NorenApi.__init__(self, host='https://piconnect.flattrade.in/PiConnectTP/', websocket='wss://piconnect.flattrade.in/PiConnectWSTp/', eodhost='https://web.flattrade.in/chartApi/getdata/')
        NorenApi.__init__(self, host='https://piconnect.flattrade.in/PiConnectTP/', websocket='wss://piconnect.flattrade.in/PiConnectWSTp/')
        NorenApi.set_session(self,userid= userid, password = password, usertoken= token)




class Flat_Trade_Login(BaseLogin):
    
    def __init__(self):
        BaseLogin.__init__(self)
        pass
    
    # @classmethod
    def login(self,credentials):
        is_login = False
        broker_session = None
        sleep_time = 5
        while not is_login :
            try :
                api_key = credentials['consumer_key']
                api_secret = credentials['secretKey']
                userid = credentials[F.USER]
                password = credentials['login_password']
                with open(Path.config_Token + f'{dt.now().date()}.txt','r') as file:
                            token = file.read()
                            file.close()
 
                broker_session = FlatTradeAPI(userid,password,token)
                session_validation_key = broker_session._NorenApi__username
                check_validation_key = credentials['session_validation_key']
                if session_validation_key == check_validation_key:
                    is_login = True
                    self.setBrokerHandle(credentials[F.USER],broker_session)
                    logging.info('Login Sucessfully')
                    return is_login, broker_session
                    # self.setAccessToken(session_validation_key)
                    
                else : 
                    time.sleep(sleep_time)
                    sleep_time +=5
                    self.login()

            except FileNotFoundError:
                session_validation_key, broker_session = Flat_Trade_Login.process(credentials)
                check_validation_key = credentials['session_validation_key']
                if session_validation_key == check_validation_key:
                    is_login = True
                    self.setBrokerHandle(credentials[F.USER],broker_session)
                    logging.info('Login Sucessfully')
                    return is_login, broker_session
                    # self.setAccessToken(session_validation_key)
                    
                else : 
                    time.sleep(sleep_time)
                    sleep_time +=5
                    self.login()

            
    # @classmethod
    def process(credentials):
        try : 
            api_key = credentials['consumer_key']
            api_secret = credentials['secretKey']
            userid = credentials[F.USER]
            password = credentials['login_password']
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.get(f'https://auth.flattrade.in/?app_key={api_key}')
            time.sleep(5)
            user_id_input = driver.find_element(By.ID, 'input-19')
            user_id_input.send_keys(userid)
            password_input = driver.find_element(By.ID, 'pwd')
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            
            time.sleep(2)
            otp = pyotp.TOTP(credentials['two_factor_code']).now()
            
            totp_input = driver.find_element(By.ID, 'pan')
            totp_input.send_keys(otp)
            
            login_button = driver.find_element(By.ID,"sbmt")
            login_button.click() 
            time.sleep(5)
            logging.info('TOPT Verification Complet')
            
            current_url = driver.current_url
            if 'code' in current_url:
                parsed_url = urlparse(current_url)
                query_parms = parse_qs(parsed_url.query)
                request_code = query_parms.get('code',[None])[0]
                f_api_secret = api_key + request_code + api_secret
                f_api_secret = hashlib.sha256(f_api_secret.encode()).hexdigest()
                payload = {'api_key':api_key,'request_code':request_code,'api_secret':f_api_secret}
                url3 = 'https://authapi.flattrade.in/trade/apitoken'
                request3 = requests.post(url3,json=payload)
                # print(request3.json())

                token = request3.json()['token']
                
                
                with open(Path.config_Token + f'{dt.now().date()}.txt','w') as file:
                    file.write(str(token))
                    file.close()

                if token == '':
                    logging.info('Token Genrtion Failed')
                else :
                    client = FlatTradeAPI(userid,password,token)
                    logging.info('Token Genrated Sucessfully')
                    return client._NorenApi__username, client
                
        except FileNotFoundError:
            logging.info('File Not Found')
    
        except Exception as e:
            logging.info(e)
            
        finally:
            # driver.quit()
            pass
    

 
            
        