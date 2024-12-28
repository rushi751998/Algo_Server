import os
class Path:
    log : str
    
    config : str
    config_BTST : str
    config_Fixed_SL : str
    config_Login : str
    config_Range_Breakout : str
    config_STBT : str
    
    order_book : str
    order_book_Broker_Orders : str
    order_book_DB_Orders : str
    
    plot : str
    plot_Available_Margin : str
    plot_PL_Recording : str
    
    
    def load():
        base_path = ''
    
        Path.log = base_path + 'log/'
        
        Path.config = base_path + 'Config/'
        Path.config_Login = Path.config + 'Login/'
        Path.config_BTST = Path.config + 'BTST/'
        Path.config_STBT = Path.config + 'STBT/'
        Path.config_Fixed_SL = Path.config + 'Fixed_SL/'
        Path.config_Range_Breakout = Path.config + 'Range_Breakout/'
        Path.config_Token = Path.config + 'Token/'
        Path.config_Scripts = Path.config + 'Scripts/'
        
        Path.order_book = base_path + 'Order_Book/'
        Path.order_book_Broker_Orders = Path.order_book + 'Broker_Orders/'
        Path.order_book_DB_Orders = Path.order_book + 'DB_Orders/'
        
        Path.plot = base_path + 'Plots/'
        Path.plot_Available_Margin = Path.plot + 'Available_Margin/'
        Path.plot_PL_Recording = Path.plot + 'PL_Recording/'
        
        all_paths = [Path.log, 
                     Path.config, 
                     Path.config_BTST,
                     Path.config_Fixed_SL, 
                     Path.config_Login, 
                     Path.config_Range_Breakout, 
                     Path.config_STBT, 
                     Path.order_book, 
                     Path.order_book_Broker_Orders, 
                     Path.order_book_DB_Orders, 
                     Path.plot, 
                     Path.plot_Available_Margin, 
                     Path.plot_PL_Recording,
                     Path.config_Token]
        for i in all_paths:
            os.makedirs(i, exist_ok=True)
            pass
        