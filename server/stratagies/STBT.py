from .base_stratagy import Base_Stratagy
from ..Utils.Fields import F
from ..Utils.Utils import Env
from ..loginmgmt.session_manger import SessionManager
from datetime import datetime as dt
from ..Utils.Ticker_Selection import Less_Than_Premium, Get_LTP
from ..Utils.Ticker_Selection import token_to_ticker,option_chain

from server.models.OrderStatus import OrderStatus
from server.models.OrderType import OrderType
from server.models.ProductType import ProductType
from server.models.Direction import Direction
from server.models.Segment import Segment
from server.core.handler import SessionHandler

import time,logging

class STBT(Base_Stratagy) :
    
    def __init__(self,config,order_book,db_orders):
        super().__init__() 
        self.Name = F.STBT
        self.config = config
        self.order_book = order_book
        self.db_orders = db_orders
    
    def Process(self):
        # self.db.drop()
        self.find_trigger()
        self.validate_order(self.order_book,self.db_orders,self.Name)
        self.place_sl_order()
        self.is_sl_exitst()
        self.is_lpt_above_sl()
        
        # self.check_sl_hit()

    def find_trigger(self):
        for stratagy in self.config:
            if dt.now() > self.config[stratagy][F.ENTRY_TIME] and not self.config[stratagy][F.TRADED]:
                print(stratagy)
                self.place_trigger_order(self.config[stratagy])
                Env.stratagy_config[self.Name][stratagy][F.TRADED] = True
                break
                
    def place_trigger_order(self,stratagy_config):
        tickers = Less_Than_Premium(stratagy_config[F.PRICE])
        ltp = 100
        for ticker in tickers:
            tag = stratagy_config[F.STRATAGY] + '//' + ticker +'//' + str(round(time.time()))[-6:]
            price = ltp * ((100 - stratagy_config[F.WAIT_PERCENT])/100)
            qty = Env.LOT_SIZE * SessionManager.User_Config[stratagy_config[F.STRATAGY]+'_qty'][Env.DTE]
            product_type  =  ProductType.MIS
            segment =  Segment.FNO
            order_type  =  OrderType.SL_LIMIT
            
            if qty > 0:
                order = {
                    F.DIRECTION : stratagy_config[F.DIRECTION],
                    F.TICKER : ticker,
                    F.PRICE : price,
                    F.PRODUCT_TYPE : product_type,
                    F.SEGEMENT : segment,
                    F.ORDER_TYPE : order_type,
                    F.QTY : qty,
                    F.TAG : tag
                }
                
                orderid, placed = SessionHandler.broker.Place_Order(order)
                if placed :
                    order = { 
                            F.ENTRY_TIME : str(dt.now()),
                            F.TICKER : ticker,
                            F.TOKEN : 0,
                            F.DIRECTION : stratagy_config[F.DIRECTION],
                            F.PRODUCT_TYPE : product_type,
                            F.SEGEMENT : segment,
                            F.OPTION_TYPE : option_chain[ticker][F.OPTION_TYPE],
                            F.QTY : qty,
                            #-------------- Entry order details -------------
                            F.ENTRY_ORDERID : orderid,
                            F.ENTRY_STATUS  : OrderStatus.VALIDATION_PENDING,
                            F.ENTRY_PRICE : price,
                            F.ENTRY_PRICE_INITIAL : price,
                            F.ENTRY_TAG : tag,
                            F.ENTRY_COUNT : 0,
                            F.ENTRY_TYPE : OrderType.LIMIT,
                            #-------------- sl order details -------------
                            F.EXIT_ORDERID : None,
                            F.EXIT_STATUS : None,
                            F.EXIT_PRICE : 0,
                            F.EXIT_PRICE_INITIAL : 0,
                            F.EXIT_TAG : None,  
                            F.EXIT_TIME: None,
                            F.EXIT_REASON : None,
                            F.EXIT_COUNT : 0,
                            F.EXIT_TYPE : None,
                            #-------- Other parameter --------------
                            F.STRATAGY : stratagy_config[F.STRATAGY],
                            F.BASE_STRATAGY : self.Name,
                            F.INDEX : None,
                            F.INDEX : Env.INDEX,
                            F.DTE : Env.DTE,
                            F.EXIT_PERCENT : stratagy_config[F.EXIT_PERCENT],
                            F.CHARGES : 0,
                            F.DRIFT_PT : 0,
                            F.DRIFT_RS : 0,
                            F.PL : 0,
                            F.RECORDING: [
                                # {'Time':'10:15:00','pl':100},
                                ]
                            }
                    
                    # print(order)
                    self.db.insert_one(order)
                    logging.info('Trade Storead in DB')
            
    def place_sl_order(self):
        try :
            order_book = self.db_orders[self.db_orders[F.EXIT_STATUS] == OrderStatus.NOT_PLACED]
            for _,row in order_book.iterrows():
                direction = self.change_direction(row[F.DIRECTION])
                ticker = row[F.TICKER]
                exit_price = round(row[F.ENTRY_PRICE] * ((100 + row[F.EXIT_PERCENT])/100),1)
                product_type = row[F.PRODUCT_TYPE]
                segment = row[F.SEGEMENT]
                qty = row[F.QTY]
                tag = row[F.ENTRY_TAG] + '_SL'
                order = {
                        F.DIRECTION : direction ,
                        F.TICKER : ticker,
                        F.PRICE : exit_price,
                        F.PRODUCT_TYPE : product_type,
                        F.SEGEMENT : segment,
                        F.ORDER_TYPE : OrderType.SL_LIMIT,
                        F.QTY : qty,
                        F.TAG : tag
                    }
                # print(order)
                orderid = SessionHandler.broker.place_Order(order)
                
                self.db.update_one({F.ENTRY_ORDERID : row[F.ENTRY_ORDERID]},{"$set" :{
                                                                                    F.EXIT_PRICE :exit_price,
                                                                                    F.EXIT_PRICE_INITIAL :exit_price,
                                                                                    F.EXIT_ORDERID :'orderid',
                                                                                    F.EXIT_TAG :tag,
                                                                                    F.EXIT_PRICE_INITIAL :exit_price,
                                                                                    F.EXIT_STATUS :OrderStatus.VALIDATION_PENDING
                                                                                    }})
                
        except Exception as e :
            print(f'Problem in Fixed_SL.place_sl_order {e}')

        # Check is entry order status in complete if yes then place sl
        
    def validate_order(self,order_book,db_orders,base_stratagy:str):
        try :
            db_orders = db_orders[(db_orders[F.BASE_STRATAGY] == base_stratagy) & ((db_orders[F.ENTRY_STATUS] == OrderStatus.VALIDATION_PENDING) | (db_orders[F.EXIT_STATUS] == OrderStatus.VALIDATION_PENDING))]
            if len(db_orders)>0 :
                for _, row in db_orders.iterrows():
                    if row[F.ENTRY_STATUS] == OrderStatus.VALIDATION_PENDING:
                        if order_book[order_book[F.ORDERID] == row[F.ENTRY_ORDERID]].iloc[0][F.ORDER_STATUS] == OrderStatus.COMPLETE :
                            self.db.update_one({F.ENTRY_ORDERID: row[F.ENTRY_ORDERID]}, { "$set": {F.ENTRY_STATUS : OrderStatus.COMPLETE,F.EXIT_STATUS : OrderStatus.NOT_PLACED}})
                            logging.info(f'Order Placed in Broker end : {row[F.ENTRY_ORDERID]}...  Wating for placing SL...')
                            
                    elif row[F.EXIT_STATUS] == OrderStatus.VALIDATION_PENDING:
                        if order_book[order_book[F.ORDERID] == row[F.ENTRY_ORDERID]].iloc[0][F.ORDER_STATUS] == OrderStatus.COMPLETE :
                            self.db.update_one({F.ENTRY_ORDERID: row[F.ENTRY_ORDERID]}, { "$set": {F.EXIT_STATUS : OrderStatus.OPEN}})
                            logging.info(f'Order Placed in Broker end : {row[F.EXIT_ORDERID]}...')

        except Exception as e :
            print(f'Problem in Fixed_SL.validate_order {e}')
    
    def check_sl_hit(self):
        db_orders = db_orders[(db_orders[F.BASE_STRATAGY] == self.Name) & (db_orders[F.EXIT_STATUS] == OrderStatus.OPEN)]
        for _, row in db_orders.iterrows():
            if self.order_book[self.order_book[F.ORDERID] == row[E.EXIT_ORDERID]].iloc[0][F.ORDER_STATUS] == OrderStatus.COMPLETE:
                self.db.update_one({F.ENTRY_ORDERID: row[F.ENTRY_ORDERID]}, { "$set": {F.EXIT_STATUS : OrderStatus.CLOSED,F.EXIT_REASON : TradeExitReason.SL_HIT}})
                logging.info(f'SL Hit : {row[F.EXIT_ORDERID]}')