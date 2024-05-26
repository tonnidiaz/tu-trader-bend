import traceback
from flask_jwt_extended import create_access_token
import pandas as pd
import pandas_ta as pta
import numpy as np
from models.app_model import App
from utils.constants import *
import os, time, json
import hashlib
import hmac
import base64, requests
from datetime import datetime
import os


def tu_path(pth: str):
    return os.path.join(*pth.split("/"))

date_str = "2024-04-28 02:00:00"
def date_str_to_timestamp(date_str: str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    timestamp = round(date_obj.timestamp() * 1000)
    return timestamp

def is_dev():
    return os.environ['ENV'] != 'prod'

def parse_klines(klines):
    """KLINES SHOULD COME IN SORTED [REVERSED] IF NEED BE"""

    # Grab only 7 columns
    klines = list(map(lambda x: x[0: 6], klines))
    df = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'], dtype=float)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def zlsma(df: pd.DataFrame, length = 32, offset = 0):
    src = df['close']
    lsma = pta.linreg(src, length, offset)
    lsma2 = pta.linreg(lsma, length, offset)
    zlsma = None
    if lsma is not None and lsma2 is not None:
        eq= lsma-lsma2
        zlsma = lsma+eq
    return zlsma

def err_handler(e: Exception):

    print(e)
    # Get the exception traceback
    tb = traceback.extract_tb(e.__traceback__)
    # Extract the last entry in the traceback
    filename, lineno, _, _ = tb[-1]
    # Print filename and line number
    print("Exception occurred in file:", filename, f"line {lineno}")

def tuned_err(code = 500, msg = "Something went wrong"):
    return f"tuned:{msg}", code



def chandelier_exit(df : pd.DataFrame, length = 1, mult = 1.8):

    print(f"BEGIN CE: {mult}")

    df['atr'] = pta.atr(df['high'], df['low'], df['close'], length)
    df['long_stop'] = df['close'].rolling(window=length).max() - df['atr'] * mult
    df['long_stop_prev'] = df['long_stop'].shift(1)

    df['short_stop'] = df['close'].rolling(window=length).min() + df['atr'] * mult
    df['short_stop_prev'] = df['short_stop'].shift(1)

    df['sir'] = df['buy_signal'] = df['sell_signal'] = np.nan
    sir = 1
    
    df['sma_20'] = pta.sma(df['close'], 20)
    df['sma_50'] = pta.sma(df['close'], 50)

    for i, row in df.iterrows():
        if i > 0:
            lsp = df['long_stop'][i - 1] 
            ls = df['long_stop'][i]

            # short stop
            ssp = df['short_stop'][i - 1] 
            ss = df['short_stop'][i]

            if df['close'][i - 1] > lsp:
                ls = max(ls, lsp)

            df.loc[i, 'long_stop'] = ls
            df.loc[i, 'long_stop_prev'] = lsp
            
            # short stop
            if df['close'][i - 1] < ssp:
                ss = min(ss, ssp)
            
            df.loc[i, 'short_stop'] = ss
            df.loc[i, 'short_stop_prev'] = ssp
        if df['close'][i] > df['short_stop_prev'][i]:
            sir = 1
        elif df['close'][i] < df['long_stop_prev'][i]:
            sir = -1
        if i > 0:
            df.loc[i, 'sir']= sir
            df.loc[i, 'buy_signal'] = int(df['sir'][i] == 1 and df['sir'][i - 1] == -1)
            df.loc[i, 'sell_signal'] = int(df['sir'][i] == -1 and df['sir'][i - 1] == 1)

    df['zlsma'] = zlsma(df)
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'atr', 'sma_20', 'sma_50', 'buy_signal','sell_signal']]
    
    print("CE COMPLETE")
    return df
 
def heikin_ashi(data : pd.DataFrame):

    ha_data = data.copy()
    ha_close = (data['open'] + data['high'] + data['low'] + data['close']) / 4
    ha_open = (data['open'].shift(1) + data['close'].shift(1)) / 2
    ha_high = data[['high', 'close', 'open']].max(axis=1)
    ha_low = data[['low', 'close', 'open']].min(axis=1)
    
    ha_data["open"] = ha_open
    ha_data["high"] = ha_high
    ha_data["low"] = ha_low
    ha_data["close"] = ha_close

    return ha_data

cnt = 0
klines = []

def get_symbol(app: App):
    return f'{app.base}{app.ccy}'

def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def get_klines(symbol, interval, start: int, end = None, save_fp = None):
    # Get the klines since the start time
    # Get again from first[timestamp] + interval until first[timestamp] <= now <= first_timestamp + interval
    global cnt
    klines  = []
    first_timestamp = start
    print(f"GETTING KLINES FOR {interval}m")
    end = end if end is not None else datetime.now().timestamp() * 1000
    while first_timestamp <= end:
        print(f"GETTING {cnt + 1} klines...")
        print(first_timestamp)
        print(datetime.fromtimestamp(first_timestamp / 1000))
        res = requests.get(f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}&interval={interval}&start={first_timestamp}")
        #print(res.json())
        res : list = res.json()['result']['list']
        if len(res):
            
            first_timestamp = round(float(res[0][0])) + interval * 60 * 1000
            klines = [*res, *klines]
        cnt +=1
    klines.reverse()
    print("DONE")


from okx import MarketData

market_data_api = MarketData.MarketAPI(flag='1')


def get_okx_klines(end = date_str_to_timestamp('2024-05-13 10:45:00')):

    """ Returns 3 months worth of klines if 1h"""
    global klines

    print('GETTING OKX KLINES...')
    res = market_data_api.get_index_candlesticks(instId='ETH-USDT', bar="15m", after=end)
    data = res['data']
    if len(data) > 0:
        klines = [*klines,*data]
        get_okx_klines(end = data[-1][0])
    d =klines.copy()
    d.reverse()
    
    return d


def get_app():
    try:
        return App.find().run()[0]
    except Exception as e:
        print("GE T APP ERROR")
        err_handler(e)