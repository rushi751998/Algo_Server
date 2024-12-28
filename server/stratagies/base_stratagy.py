from ..Utils.Utils import database,Env
from ..Utils.Fields import F
from ..models.Direction import Direction
from ..models.OrderStatus import OrderStatus
from abc import ABC, abstractmethod
import logging

class Base_Stratagy :
    
    def __init__(self):
        self.db = database()[Env.today]
        pass
    
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
        
    
        
    def is_sl_exitst(self):
        pass
    
    def is_lpt_above_sl(self):
        pass