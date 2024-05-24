import json

from flask_socketio import emit

from models.user_model import User
from utils.io.io import socketio
from classes.binance import Binance
from strategies.ce_sma import ce_sma_backtest
from utils.functions import chandelier_exit, date_str_to_timestamp, err_handler, heikin_ashi, parse_klines, tu_path
from strategies.ce_sma_strategies import strategies as ce_sma_strategies
from utils.constants import klines_dir, dfs_dir

test = False

def on_backtest(body):
    try:
        """ username = body.get('username')
        if not username:
            emit('backtest', {'err': 'Not authenticated'})
            return """
        
        _bin: Binance = Binance.inst
        symbol = body.get('symbol')
        base_ccy = symbol.split(',')
        symbol = "".join(base_ccy)

        interval = body.get('interval')
        start = body.get('start')
        end = body.get('end')
        offline = body.get('offline')
        print(offline)
        start_ts = date_str_to_timestamp(start) if start else start
        end_ts = date_str_to_timestamp(end) if end else end
        fp = tu_path('data/klines/binance/klines.json') if False else None
        print(start, end)
        emit('backtest', 'Getting klines...')

        if test:
            print("IS TEST")
            fp = tu_path('data/klines/binance/klines.json')
            with open(fp) as f:
                klines = json.load(f)
        elif offline:
            print("IS OFFLINE")
            fp = tu_path(f"{klines_dir}/{symbol}_{interval}m")
            with open(fp) as f:
                klines = json.load(f)
        else:
            klines = _bin.get_klines(symbol, interval=interval, start=start_ts, end=end_ts, save_fp=fp)
        emit('backtest', 'Analizing data...')
        df = chandelier_exit(heikin_ashi(parse_klines(klines)))
        bal = float(body.get('bal'))

        emit('backtest', 'Backtesting...') 
        lev = body.get('lev')
        lev = int(lev) if lev else 1
        str_num = int(body.get('strategy'))
        data = ce_sma_strategies[str_num - 1].run(df, bal, lev=lev,p_gain= body.get('pGain'))#ce_sma_backtest(df, bal, lev)
        data['profit'] = round(data['balance'] - bal,2)
        data = {**data, 'base': base_ccy[0], 'ccy': base_ccy[1]}
        emit('backtest', {"data": data})
        return data 
    
    except Exception as e:
        err_handler(e)
        emit('backtest', {"err": "Something went wrong"})
        return 'Something went wrong', 500