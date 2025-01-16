from .Fields import F
import pandas as pd

ticker_to_token = {}
token_to_ticker = {}
option_type = {}
option_chain = {}

def Closest_Premium(price):
    tickers = []
    option_chain_df = pd.DataFrame(option_chain).T
    option_chain_df['distance'] = abs(option_chain_df[F.LTP]-price)
    # option_chain_df = option_chain_df[option_chain_df[F.OI]>=10000]
    for option_type in [F.CE,F.PE]:
        ce = option_chain_df[option_chain_df[F.OPTION_TYPE] == option_type]
        ce = ce[ce['distance'] == ce['distance'].min()]
        tickers.append(ce[ce['distance'] == ce['distance'].min()].index[0])
    return tickers

def Less_Than_Premium(price):
    tickers = []
    option_chain_df = pd.DataFrame(option_chain).T
    # option_chain_df = option_chain_df[option_chain_df[F.OI]>10000]
    for option_type in [F.CE,F.PE]:
        ce = option_chain_df[option_chain_df[F.OPTION_TYPE] == option_type]
        ce = ce[ce[F.LTP] <= price]
        ce.sort_values(F.LTP,inplace = True,ascending = True)
        tickers.append(ce.index[-1])
    return tickers

def Get_LTP(Ticker):
    return round(option_chain[Ticker][F.LTP])