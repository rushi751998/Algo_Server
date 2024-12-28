import logging
import pandas as pd
from ..Utils.Fields import F
from ..Utils.Utils import send_message,Env
from .BaseOrderManager import BaseOrderManager
from ..models.OrderStatus import OrderStatus
from ..models.OrderType import OrderType
from ..models.ProductType import ProductType
from ..models.Direction import Direction
from ..models.Segment import Segment
from ..models.RejectionReason import Rejection_Reason
from ..loginmgmt.session_manger import SessionManager

class FlatTrade(BaseOrderManager):
    name = F.FLAT_TRADE
    Ticker_TO_Token = {}
    
    def __init__(self):
        super.__init__()
        

    @staticmethod
    def Place_Order(order):
        user = SessionManager.User_Config
        logging.info(f'Placing Order-request : {order}')
        print(f'Placing Order-request : {order}')
        # product_type =  product_type if product_type != None else Env.product_type
        # print('\nbuy_or_sell : ',FlatTrade.convert_Direction(order[F.DIRECTION]), 
        #         '\nproduct_type : ',FlatTrade.convert_Product_Type(order[F.PRODUCT_TYPE]), 
        #         '\nexchange : ',FlatTrade.convert_segment(order[F.SEGEMENT]), 
        #         '\ntradingsymbol : ',order[F.TICKER],
        #         '\nquantity : ',order[F.QTY], 
        #         '\ndiscloseqty : ',0, 
        #         '\nprice_type : ',FlatTrade.convert_Order_Type(order[F.ORDER_TYPE]), 
        #         '\nprice : ',order[F.PRICE], 
        #         '\ntrigger_price : ',order[F.PRICE],
        #         '\nretention : ','DAY', 
        #         '\nremarks : ',order[F.TAG])
        responce = user[F.SESSION].place_order(
                                                buy_or_sell = FlatTrade.convert_Direction(order[F.DIRECTION]), 
                                                product_type = FlatTrade.convert_Product_Type(order[F.PRODUCT_TYPE]), 
                                                exchange = FlatTrade.convert_segment(order[F.SEGEMENT]), 
                                                tradingsymbol = order[F.TICKER],
                                                quantity = order[F.QTY], 
                                                discloseqty = 0, 
                                                price_type = FlatTrade.convert_Order_Type(order[F.ORDER_TYPE]), 
                                                price = order[F.PRICE], 
                                                trigger_price = order[F.PRICE]-0.5 if order[F.DIRECTION] == Direction.LONG  else  order[F.PRICE] +0.5,
                                                retention = 'DAY', 
                                                remarks = order[F.TAG]
                                            )
        
        print(responce)
        if responce['stat'] == 'Ok' :
            logging.info(f'Placed MIS Order Sucessfully... Responce : {responce}')
            return responce['norenordno'] , True
        else :
            logging.warning(f'Faild MIS Order\n{user[F.USER]}\nParam : {order}\nResponce : {responce}')
            responce , False
    
    @staticmethod
    def modify_Order(order):
        user = SessionManager.User_Config
        logging.info(f'Modify Order-request {order}')
        responce = user[F.SESSION].modify_order(
                                                exchange=FlatTrade.convert_segment(order[F.SEGEMENT]), 
                                                tradingsymbol=order[F.TICKER], 
                                                orderno=order[F.ORDERID],
                                                newquantity=order[F.QTY], 
                                                newprice_type=FlatTrade.convert_Order_Type(order[F.ORDER_TYPE]),
                                                newprice=order[F.PRICE],  
                                                newtrigger_price=order[F.PRICE]-0.5 if order[F.DIRECTION] == Direction.LONG  else  order[F.PRICE] +0.5,
                                                )

        try : 
            if responce['stat'] == 'Ok' :
                logging.info(f'Modified Sucessfully: {responce}')
                return True
            else : 
                logging.warning(f'Not able to Modify: {responce}')
                return False

        except Exception as e : 
            return False

    @staticmethod
    def modify_Order_To_Market(order):
        user = SessionManager.User_Config
        logging.info(f'Modify Market Order-request {order}')
        
        responce = user[F.SESSION].modify_order(
                                                exchange=FlatTrade.convert_segment(order[F.SEGEMENT]), 
                                                tradingsymbol=order[F.TICKER], 
                                                orderno=order[F.ORDERID],
                                                newquantity=order[F.QTY], 
                                                newprice_type=FlatTrade.convert_Order_Type(OrderType.MARKET), 
                                                newprice=0
                                                )
        try : 
            if responce['stat'] == 'Ok' :
                logging.info(f'Modified Sucessfully: {responce}')
                return True
            else : 
                logging.warning(f'Not able to Modify: {responce}')
                return False

        except Exception as e : 
            return False

    @staticmethod
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

    @staticmethod
    def get_available_margin():
        user = SessionManager.User_Config
        return float(user[F.SESSION].limits()['Net'])
    
    # def is_order_rejected_func(order_id):
    #     user = SessionManager.User_Config
    #     time.sleep(3)
    #     all_orders = KotakManager.Order_book()
    #     order_status = all_orders[all_orders[F.ORDERID] == str(order_id)].iloc[0]
        
    #     if order_id != 0 : 
    #         if order_status[F.ORDER_STATUS] == OrderStatus.REJECTED:
    #             if ('MIS PRODUCT TYPE BLOCKED'.lower() in order_status["message"].lower()) or ('MIS TRADING NOT ALLOWED'.lower() in order_status["message"].lower()) : 
    #                 send_message(message = f'Order rejected\nOrder ID : {order_id}\nProduct Type : {Env.product_type}\nMessage : {order_status["message"]}\nPlacing NRML order..', emergency = True)
    #                 return True, True
    #             # add more rejection types here
    #             else : 
    #                 send_message(message = f'Order rejected\nOrder ID : {order_id}\nProduct Type : {Env.product_type}\nMessage : {order_status["message"]}', emergency = True)
    #                 return True, False
                    
    #         else : 
    #             return False, False
                
    @staticmethod
    def Order_book():
        user = SessionManager.User_Config
        try :
            responce = user[F.SESSION].get_order_book()
            # if responce['stat'] == 'Ok' : 
            all_orders = pd.DataFrame(responce)
            all_orders = FlatTrade.rename(all_orders)[[F.ORDERID,F.SEGEMENT,F.TICKER,F.TOKEN,F.QTY,F.PRODUCT_TYPE,F.MESSAGE,'instname','dname',F.PRICE,F.ORDER_STATUS,F.ORDER_TIME,F.FILLED_QTY]]
            all_orders[[F.INDEX,F.EXPIRY_DATE,F.STRIKE_PRICE,F.OPTION_TYPE]] = (all_orders['dname'].str.strip().str.split(' ',expand = True))
            # all_orders[F.SEGEMENT].replace(FlatTrade.segment_dict, inplace=True)
            all_orders.replace({F.ORDER_STATUS:{'REJECTED': OrderStatus.REJECTED,
                                                'COMPLETE': OrderStatus.COMPLETE,
                                                'OPEN': OrderStatus.OPEN,
                                                'TRIGGER_PENDING': OrderStatus.TRIGGER_PENDING,
                                                'CANCELLED' : OrderStatus.CANCELLED
                                                }}, inplace=True)
            
            
            
            
            # all_orders[F.ORDER_STATUS].replace({'REJECTED': OrderStatus.REJECTED,
            #                                     'COMPLETE': OrderStatus.COMPLETE,
            #                                     'OPEN': OrderStatus.OPEN,
            #                                     'TRIGGER_PENDING': OrderStatus.TRIGGER_PENDING,
            #                                     'CANCELLED' : OrderStatus.CANCELLED
            #                                     }, inplace=True)
            
            all_orders[F.ORDER_TIME] = pd.to_datetime(all_orders[F.ORDER_TIME], format="%H:%M:%S %d-%m-%Y")
            # all_orders[F.ORDER_TIME] = pd.to_datetime(all_orders[F.ORDER_TIME],"%H:%M:%S %d-%m-%Y")
            # all_orders[F.ORDER_TIME] = all_orders[F.ORDER_TIME].apply()
            
            # all_orders[F.TRANSACTION_TYPE].replace(FlatTrade.transaction_type, inplace=True)
            return all_orders
                
        except Exception as e:
            send_message(message = f'Not able to get orderbook\nMessage : {e}\nresponce : {responce}', emergency = True,user=user)
            return False

    @staticmethod
    def convert_Product_Type(productType):
        if productType == ProductType.MIS:
            return "I"
        elif productType == ProductType.NRML:
            return "M"
        elif productType == ProductType.CNC:
            return "C"
        elif productType == ProductType.CO:
            return "H"
        return None  

    @staticmethod
    def convert_Order_Type(orderType):
        if orderType == OrderType.LIMIT:
            return "LMT"
        elif orderType == OrderType.MARKET:
            return "MKT"
        elif orderType == OrderType.SL_MARKET:
            return "SL-MKT"
        elif orderType == OrderType.SL_LIMIT:
            return "SL-LMT"
        return None

    @staticmethod
    def convert_Direction(direction):
        if direction == Direction.LONG:
            return 'B'

        elif direction == Direction.SHORT:
            return 'S'
        return None
    
    @staticmethod
    def convert_segment(segment):
        if segment == Segment.FNO:
            return "NFO" if Env.INDEX  in [F.NIFTY,F.BANKNIFTY,F.MIDCPNIFTY,F.FINNIFTY,F.NIFTYNXT50] else "BFO"

        elif segment == Segment.EQUITY:
            return "NSE" if Env.INDEX  in [F.NIFTY,F.BANKNIFTY,F.MIDCPNIFTY,F.FINNIFTY,F.NIFTYNXT50] else "BSE"

        elif segment == Segment.CURRENCY:
            return "cde_fo" 

        elif segment == Segment.COMMADITY:
            return "mcx_fo"
        return None
    
    @staticmethod
    def Rejection_Cause(message:str):
        if 'insufficient fund'.lower() in message.lower():
            return Rejection_Reason.INSUFFICIENT_FUND
        
        elif 'MIS not allowded'.lower() in message.lower():
            return Rejection_Reason.MIS_BLOCKED
        
        elif 'worser price'.lower() in message.lower():
            return Rejection_Reason.WORSER_PRICE
    
    @staticmethod
    def rename(df):
        column_name_dict = {
            # Order Related
            'norenordno': F.ORDERID,
            'norentm': F.ORDER_TIME,
            'tsym': F.TICKER,
            'token': F.TOKEN,
            'qty': F.QTY,
            'rqty': F.FILLED_QTY,
            'avgprc': F.PRICE,
            'trantype': F.TRANSACTION_TYPE,
            'prctyp' : F.PRODUCT_TYPE,
            'exch': F.SEGEMENT,
            'status': F.ORDER_STATUS,
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
            'rejreason' : F.MESSAGE,
            
            # Script Master
            'pSymbol' : F.TOKEN ,
            'pTrdSymbol' : F.TICKER ,
            'pSymbolName' : F.INDEX ,
            'lExpiryDate' : F.EXPIRY_DATE ,
            'dStrikePrice;' : F.STRIKE_PRICE ,
            'pOptionType' : F.OPTION_TYPE ,
            'lLotSize' : F.LOT_SIZE ,
        }
        return df.rename(columns = column_name_dict)
 