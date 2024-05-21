import json

from flask_socketio import emit

from utils.io.io import socketio
from classes.binance import Binance
from routes.strategies.ce_sma import ce_sma_backtest
from utils.functions import chandelier_exit, date_str_to_timestamp, err_handler, heikin_ashi, parse_klines

test = False

def on_backtest(body):
    try:
        _bin: Binance = Binance.inst
        symbol = body.get('symbol')
        base_ccy = symbol.split(',')
        symbol = "".join(base_ccy)
        start = body.get('start')
        end = body.get('end')

        start = date_str_to_timestamp(start) if start else start
        end = date_str_to_timestamp(end) if end else end
        fp = 'data/klines/binance/klines.json' if False else None
        print(start, end)
        emit('backtest', 'Getting klines...')
        if test:
            print("IS TEST")
            fp = 'data/klines/binance/klines.json'
            with open(fp) as f:
                klines = json.load(f)
        else:
            klines = _bin.get_klines(symbol, interval=body.get('interval'), start=start, end=end, save_fp=fp)
        emit('backtest', 'Analizing data...')
        df = chandelier_exit(heikin_ashi(parse_klines(klines)))
        bal = float(body.get('bal'))

        emit('backtest', 'Backtesting...') 
        lev = body.get('lev')
        lev = int(lev) if lev else 1

        data = ce_sma_backtest(df, bal, lev)
        data['profit'] = round(data['balance'] - bal,2)
        data = {**data, 'base': base_ccy[0], 'ccy': base_ccy[1]}
        emit('backtest', {"data": data})
        return data
    
    except Exception as e:
        err_handler(e)
        emit('backtest', {"err": "Something went wrong"})
        return 'Something went wrong', 500