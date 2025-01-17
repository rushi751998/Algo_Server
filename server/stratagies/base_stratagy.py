from ..Utils.Utils import database,Env
from ..Utils.Fields import F
from ..models.Direction import Direction
from ..models.OrderStatus import OrderStatus
from ..Utils.Ticker_Selection import Get_LTP
from server.core.handler import SessionHandler
from server.models.OrderType import OrderType
from server.models.TradeExitReason import TradeExitReason
from datetime import datetime as dt
from abc import ABC, abstractmethod
import logging

class Base_Stratagy :
    
    def __init__(self,order_book,db_orders):
        self.order_book = order_book
        self.db_orders = db_orders
        self.db = database()[Env.today]
    
    @abstractmethod
    def Process(self):
        pass
    
    @abstractmethod
    def find_trigger(self):
        pass
    
    def place_recording_order(self):
        pass
    
    @abstractmethod
    def place_trigger_order(self):
        pass
    
    @abstractmethod
    def place_sl_order(self):
        pass

    @abstractmethod        
    def check_sl_hit(self):
        pass
    
    # def get_config(self,stratagy):
    #     pass
    
    # def can_trade(self,stratagy):
    #     pass
    
    def db():
        return database()[Env.today]
    
    def change_direction(self,direction):
        if direction == Direction.LONG:
            return Direction.SHORT 
        elif direction == Direction.SHORT:
            return Direction.LONG 
        else: 
            return None
    
    def find_exit(self,base_stratagy:str):
        order_book = self.order_book
        db_orders = self.db_orders
        sub_stratagy =  Env.stratagy_config[base_stratagy]
        for i in sub_stratagy:
            db_orders = db_orders[(db_orders[F.STRATAGY] == sub_stratagy[i][F.STRATAGY]) & (db_orders[F.EXIT_STATUS] == OrderStatus.OPEN)]
            if (sub_stratagy[i][F.EXIT_TIME]>dt.now()) & (len(db_orders)>0):
                for _,row in db_orders.iterrows():
                    count = row[F.EXIT_COUNT]
                    order_status = order_book[order_book[F.ORDERID]==row[F.EXIT_ORDERID]].iloc[0][F.ORDER_STATUS]
                    
                    if order_status == OrderStatus.COMPLETE :
                        exit_price = order_book[order_book[F.ORDERID]==row[F.EXIT_ORDERID]].iloc[0][F.PRICE]
                        exit_type = order_book[order_book[F.ORDERID]==row[F.EXIT_ORDERID]].iloc[0][F.ORDER_TYPE]
                        self.db.update_one({F.EXIT_ORDERID : row[F.EXIT_ORDERID]},{"$set" :{
                                                                                        F.EXIT_PRICE : exit_price,
                                                                                        F.EXIT_TYPE : exit_type,
                                                                                        F.EXIT_STATUS : OrderStatus.CLOSED,
                                                                                        F.EXIT_REASON : TradeExitReason.SQUARE_OFF,
                                                                                        }})
                        
                    elif (order_status in [OrderStatus.TRIGGER_PENDING,OrderStatus.OPEN]) & (count<3):
                        ltp = Get_LTP(row[F.TICKER])
                        order = {F.SEGEMENT: row[F.SEGEMENT],
                                F.TICKER: row[F.TICKER],
                                F.ORDERID: row[F.EXIT_ORDERID],
                                F.QTY: row[F.QTY],
                                F.ORDER_TYPE: OrderType.LIMIT ,
                                F.PRICE: ltp ,
                                F.DIRECTION: self.change_direction(row[F.DIRECTION])
                                }
                        
                        is_modified = SessionHandler.broker.modify_Order(order)
                        if is_modified:
                            self.db.update_one({F.EXIT_ORDERID : row[F.EXIT_ORDERID]},{"$set" :{
                                                                                        F.EXIT_PRICE_INITIAL : ltp,
                                                                                        F.EXIT_COUNT : count+1
                                                                                        }})
                    else:
                        order = {F.SEGEMENT: row[F.SEGEMENT],
                                F.TICKER: row[F.TICKER],
                                F.ORDERID: row[F.EXIT_ORDERID],
                                F.QTY: row[F.QTY]
                                }
                        
                        is_modified = SessionHandler.broker.modify_Order_To_Market(order)
                        if is_modified:
                            self.db.update_one({F.EXIT_ORDERID : row[F.EXIT_ORDERID]},{"$set" :{
                                                                                        F.EXIT_COUNT : count+1
                                                                                        }})
                        
                    
    
        
    def is_sl_exitst(self):
        pass
    
    def is_lpt_above_sl(self):
        pass