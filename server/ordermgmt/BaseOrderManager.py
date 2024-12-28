

from abc import ABC,abstractmethod

class BaseOrderManager(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def place_Order(orderInputParams):
        pass

    @abstractmethod
    def modify_Order(orderModifyParams):
        pass

    @abstractmethod
    def modify_Order_To_Market(order):
        pass

    @abstractmethod
    def cancel_Order(order):
        pass
    
    @abstractmethod
    def get_available_margin(user):
        pass
    
    @abstractmethod
    def Order_book(user):
        pass

    @abstractmethod
    def convert_Product_Type(productType):
        pass

    @abstractmethod
    def convert_Order_Type(orderType):
        pass

    @abstractmethod
    def convert_Direction(direction):
        pass

    @abstractmethod
    def convert_segment(segment):
        pass

    @abstractmethod
    def rename(df):
        pass