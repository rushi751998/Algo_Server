import neo_api_client
import logging
import pandas as pd
from ..Utils.Fields import F
from ..Utils.Utils import send_message
from .BaseOrderManager import BaseOrderManager
from ..models.OrderStatus import OrderStatus
from ..models.OrderType import OrderType
from ..models.ProductType import ProductType
from ..models.Direction import Direction
from ..models.Segment import Segment
from ..loginmgmt.session_manger import SessionManager

class KotakManager(BaseOrderManager):
    name = F.KOTAK_NEO
    Ticker_TO_Token = {}
    
    def __init__(self):
        super.__init__()
        

    @staticmethod
    def place_Order(order):
        user = SessionManager.User_Config
        product_type =  product_type if product_type != None else Env.product_type
        # print('product_type : ', product_type)
        responce = user[F.SESSION].place_order(
                                                product = KotakManager.convert_Product_Type(order[F.PRODUCT_TYPE]), 
                                                price = str(order[F.PRICE]), 
                                                trigger_price = str(trigger_price), 
                                                order_type = KotakManager.convert_Order_Type(order[F.ORDER_TYPE]), 
                                                quantity = str(order[F.QTY]), 
                                                trading_symbol = order[F.TICKER],
                                                transaction_type = KotakManager.convert_Direction(order[F.DIRECTION]),
                                                amo = "NO", 
                                                disclosed_quantity = "0", 
                                                market_protection = "0", 
                                                pf = "N", 
                                                validity = "DAY",
                                                exchange_segment = KotakManager.convert_exchange(order[F.SEGEMENT]),
                                                tag = order[F.TAG]
                                            )
        if responce['stCode'] == 200 :
            logging.info(f'Placed MIS Order\n{user[F.USER]}\nParam : {order}\nResponce : {responce}')
            return responce['nOrdNo'] , True
        else :
            logging.warning(f'Faild MIS Order\n{user[F.USER]}\nParam : {order}\nResponce : {responce}')
            responce , False

    def modify_Order(order):
        user = SessionManager.User_Config
        responce = user[F.SESSION].modify_order(order_id = order_id, 
                                            price = str(new_price), 
                                            quantity = str(quantity), 
                                            trigger_price = str(trigger_price if trigger_price != None else new_price-0.05), 
                                            validity = "DAY", order_type = order_type, amo = "NO")
        logging.info(f'Modify Order \n{user[F.USER]}\n{orderInputParams}\n{responce}')
        try : 
            if responce['stCode'] == 200 :
                return True, responce[F.nOrdNo], "Placed Sucessfully"
            else : 
                return False, order_id, str(responce['Error'])
        except Exception as e : 
            return False,order_id , str(responce['Error'])

    def modify_Order_To_Market(order):
        user = SessionManager.User_Config
        responce = user[F.SESSION].modify_order(order_id = order['order_id'], 
                                            new_price = 0, 
                                            quantity = order['qty'], 
                                            trigger_price = 0, 
                                            order_type = KotakManager.convert_Order_Type(OrderType.MARKET))

    def cancel_Order(order):
        user = SessionManager.User_Config
        responce = user[F.SESSION].cancel_order(order_id = order_number)
        logging.info(f'cancel_order : {responce}\n')
        try : 
            if responce['stCode'] == 200 :
                return True,responce['result'],"Placed Sucessfully"
            else : 
                return False,0,responce['errMsg']
        except Exception as e : 
            return False,order_id , str(responce)#['Error']

    def get_available_margin():
        user = SessionManager.User_Config
        return float(user[F.SESSION].limits()['Net'])
    
    def is_order_rejected_func(order_id):
        user = SessionManager.User_Config
        time.sleep(3)
        all_orders = KotakManager.Order_book()
        order_status = all_orders[all_orders[F.ORDERID] == str(order_id)].iloc[0]
        
        if order_id != 0 : 
            if order_status[F.ORDER_STATUS] == OrderStatus.REJECTED:
                if ('MIS PRODUCT TYPE BLOCKED'.lower() in order_status["message"].lower()) or ('MIS TRADING NOT ALLOWED'.lower() in order_status["message"].lower()) : 
                    send_message(message = f'Order rejected\nOrder ID : {order_id}\nProduct Type : {Env.product_type}\nMessage : {order_status["message"]}\nPlacing NRML order..', emergency = True)
                    return True, True
                # add more rejection types here
                else : 
                    send_message(message = f'Order rejected\nOrder ID : {order_id}\nProduct Type : {Env.product_type}\nMessage : {order_status["message"]}', emergency = True)
                    return True, False
                    
            else : 
                return False, False
                
    @staticmethod
    def Order_book():
        user = SessionManager.User_Config
        try :
            responce = user[F.SESSION].order_report()
            if responce['stCode'] == 200 : 
                all_orders = pd.DataFrame(responce['data'])[['nOrdNo','ordDtTm','trdSym','tok','qty','prcTp','fldQty','avgPrc','trnsTp','prod' ,'exSeg','ordSt','stkPrc','optTp','brdLtQty','expDt','GuiOrdId','rejRsn']]
                all_orders = KotakManager.rename(all_orders)
                all_orders[F.SEGEMENT].replace(KotakManager.segment_dict, inplace=True)
                all_orders[F.ORDER_STATUS].replace({'rejected': OrderStatus.REJECTED,
                                                    'complete': OrderStatus.COMPLETE,
                                                    'open': OrderStatus.OPEN,
                                                    'trigger pending': OrderStatus.TRIGGER_PENDING,
                                                    'cancelled' : OrderStatus.CANCELLED
                                                    }, inplace=True)
                
                all_orders[F.TRANSACTION_TYPE].replace(KotakManager.transaction_type, inplace=True)
                return all_orders
                
        except Exception as e:
            send_message(message = f'Not able to get orderbook\nMessage : {e}\nresponce : {responce}', emergency = True,user=user)
            return False

    
    @staticmethod
    def convert_Product_Type(productType):
        if productType == ProductType.MIS:
            return "MIS"
        elif productType == ProductType.NRML:
            return "NRML"
        elif productType == ProductType.CNC:
            return "CNC"
        elif productType == ProductType.CO:
            return "CO"
        return None 

    @staticmethod
    def convert_Order_Type(orderType):
        if orderType == OrderType.LIMIT:
            return "L"
        elif orderType == OrderType.MARKET:
            return "MKT"
        elif orderType == OrderType.SL_MARKET:
            return "SL-M"
        elif orderType == OrderType.SL_LIMIT:
            return "SL"
        return None

    @staticmethod
    def convert_Direction(direction):
        if direction == Direction.LONG:
            return 'Buy'

        elif direction == Direction.SHORT:
            return 'Sell'
        return None
    
    @staticmethod
    def convert_segment(segment):
        if segment == Segment.FNO:
            return "nse_fo"
        elif segment == Segment.EQUITY:
            return "nse_cm"
        elif segment == Segment.CURRENCY:
            return "cde_fo"
        elif segment == Segment.COMMADITY:
            return "mcx_fo"
        return None
    
    @staticmethod
    def Rejection_Cause(message:str):
        if 'insufficient fund'.lower() in message.lower():
            pass
        
        elif 'MIS not allowded'.lower() in message.lower():
            pass
    
    @staticmethod
    def rename(df):
        column_name_dict = {
            # Order Related
            'nOrdNo': F.ORDERID,
            'ordDtTm': F.ORDER_TIME,
            'trdSym': F.TIKCER,
            'tok': F.TOKEN,
            'qty': F.QTY,
            'fldQty': F.FILLED_QTY,
            'avgPrc': F.PRICE,
            'trnsTp': F.TRANSACTION_TYPE,
            'prod' : F.PRODUCT_TYPE,
            'exSeg': F.SEGEMENT,
            'ordSt': F.ORDER_STATUS,
            'prcTp' : F.ORDER_TYPE,
            'stkPrc': F.STRIKE_PRICE,
            # 'strike': F.strike_price,
            'optTp': F.OPTION_TYPE,
            'brdLtQty':'brdLtQty',
            'expDt': F.EXPIRY_DATE,
            'GuiOrdId': F.TAG,
            'type' : 'type',
            'buyAmt' : F.BUY_AMOUNT,
            'flBuyQty' : F.FILLED_BUY_QTY,
            'flSellQty' : F.FILLED_SELL_QTY,
            'sellAmt' : F.SELL_AMOUNT,
            'rejRsn' : F.MESSAGE,
            
            # Script Master
            'pSymbol' : F.TOKEN ,
            'pTrdSymbol' : F.TIKCER ,
            'pSymbolName' : F.INDEX ,
            'lExpiryDate' : F.EXPIRY_DATE ,
            'dStrikePrice;' : F.STRIKE_PRICE ,
            'pOptionType' : F.OPTION_TYPE ,
            'lLotSize' : F.LOT_SIZE ,
        }
        return df.rename(columns = column_name_dict)
        
    



