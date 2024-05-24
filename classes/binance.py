from datetime import datetime
import json
import os

import requests
from utils.functions import err_handler, get_app
from binance.client import Client

class Binance:

    inst = None
    def __init__(self) -> None:
        print("INIT BINANCE...")
        self.app = get_app()

    def get_klines(self, symbol = None, start = None, end = None, interval = None, save_fp = None):
        try:
            cnt = 0
            klines = []
            symbol = symbol if symbol else self.get_symbol()
            interval = interval if interval else self.app.interval
            interval = int(interval)
            end = end if end is not None else int(datetime.now().timestamp() * 1000)
            parsed_interval = f"{interval}m" if interval < 60 else f"{int(interval/ 60)}h"
            print(end) 
            if start is not None:
                first_timestamp = int(start)
                while first_timestamp <= end:
                    print(f"GETTING {cnt + 1} klines...")
                    print(first_timestamp)
                    print(datetime.fromtimestamp(first_timestamp / 1000))
                    res = requests.get(f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval={parsed_interval}&startTime={first_timestamp}")
                    data = res.json()
                    klines = [*klines, *data]
                    if len(data) == 0:
                        break
                    first_timestamp = int(float(data[-1][0])) + int(interval) * 60 * 1000
                    cnt += 1
            else:
                res = requests.get(f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval={parsed_interval}&endTime={end}")
                klines =  res.json()
            
            if save_fp:
                with open(save_fp, 'w') as f:
                    json.dump(klines, f)
            if type(klines) is not list:
                
                print(klines)
                raise Exception({'msg': "ERROR FETCHING KLINES"})

            print(len(klines))
            print("Done fetching klines")
            return klines
        
        except Exception as e:
            err_handler(e)
            
    def get_symbol(self):
        app = self.app
        return f'{app.base}{app.ccy}'