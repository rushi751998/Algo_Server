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
from server.models.TradeExitReason import TradeExitReason
from server.core.handler import SessionHandler

import time,logging

class Fixed_SL(Base_Stratagy) :
    
    def __init__(self,config,order_book,db_orders):
        super().__init__(order_book,db_orders) 
        self.Name = F.FIXED_SL
        self.config = config
        
    
    def Process(self):
        # self.db.drop()
        self.find_trigger()
        if len(self.db_orders)>0 :
            self.place_sl_order()
            self.is_sl_exitst()
            self.is_lpt_above_sl()
            self.validate_order(self.Name)
            self.check_sl_hit()
            # self.find_exit(self.Name)
            

    def adjust_hedge_qty(self,qty=None,db_orders=None,stratagy=None,add_hedge=False, remove_hedge=False):
        if add_hedge:
            pass
        
        elif remove_hedge:
            pass

    def find_trigger(self):
        for stratagy in self.config:
            if dt.now() > self.config[stratagy][F.ENTRY_TIME] and not self.config[stratagy][F.TRADED]:
                # headge qty calculate
                stratagy_config = self.config[stratagy]
                print(stratagy_config)
                qty = Env.LOT_SIZE * SessionManager.User_Config[stratagy_config[F.STRATAGY]+'_qty'][Env.DTE]
                
                self.adjust_hedge_qty(qty,self.db_orders,stratagy_config[F.STRATAGY],add_hedge=True)
                
                self.place_trigger_order(stratagy_config,qty)
                Env.stratagy_config[self.Name][stratagy][F.TRADED] = True
                
    def place_trigger_order(self,stratagy_config,qty):
        tickers = Less_Than_Premium(stratagy_config[F.PRICE])
        for ticker in tickers:
            ltp = Get_LTP(ticker)
            # ltp = 100
            tag = stratagy_config[F.STRATAGY] + '//' + ticker +'//' + str(round(time.time()))[-6:]
            price = round(ltp * ((100 - stratagy_config[F.WAIT_PERCENT])/100))
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
                tag = row[F.ENTRY_TAG] + '//SL'
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
                orderid, placed = SessionHandler.broker.Place_Order(order)
                
                if orderid is not None:
                
                    self.db.update_one({F.ENTRY_ORDERID : row[F.ENTRY_ORDERID]},{"$set" :{
                                                                                        F.EXIT_PRICE : exit_price,
                                                                                        F.EXIT_PRICE_INITIAL : exit_price,
                                                                                        F.EXIT_ORDERID : orderid,
                                                                                        F.EXIT_TAG : tag,
                                                                                        F.EXIT_PRICE_INITIAL : exit_price,
                                                                                        F.EXIT_STATUS : OrderStatus.VALIDATION_PENDING
                                                                                        }})
                
        except Exception as e :
            print(f'Problem in Fixed_SL.place_sl_order {e}')

        # Check is entry order status in complete if yes then place sl
        
    
    def check_sl_hit(self):
        db_orders = self.db_orders[(self.db_orders[F.BASE_STRATAGY] == self.Name) & (self.db_orders[F.EXIT_STATUS] == OrderStatus.OPEN)]
        for _, row in db_orders.iterrows():
            trade = self.order_book[self.order_book[F.ORDERID] == row[F.EXIT_ORDERID]].iloc[0]
            if trade[F.ORDER_STATUS] == OrderStatus.COMPLETE:
                self.db.update_one({F.ENTRY_ORDERID: row[F.ENTRY_ORDERID]}, { "$set": {
                                                    F.EXIT_STATUS : OrderStatus.CLOSED,
                                                    F.EXIT_REASON : TradeExitReason.SL_HIT,
                                                    F.EXIT_TYPE : trade[F.ORDER_TYPE],
                                                    F.EXIT_TIME : str(dt.now())
                                                     }})
                logging.info(f'SL Hit : {row[F.EXIT_ORDERID]}')