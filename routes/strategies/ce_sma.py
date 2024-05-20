import pandas as pd
from utils.constants import MAKER_FEE_RATE, TAKER_FEE_RATE
from data.data import data

def ce_sma_backtest(df: pd.DataFrame, balance: float, lev = 1):

    pos = False
    cnt = 0
    gain, loss =0,0
    p_gain = data.p_gain
    use_close = data.use_close
    start_bal = balance

    m_data = {'data': {}}
    print("CE_SMA: BEGIN BACKTESTING...\n")
    for i, row in df.iterrows():

        if row['buy_signal'] ==1 and not pos and ( row['sma_20'] is not None and row['sma_50'] is not None and row['sma_20'] > row['sma_50']  ) :
                pos = True
                balance *= lev
                entry_price = row['close']
                tp = entry_price * ( 1 + p_gain)
                lowest_sma = min(row['sma_20'], row['sma_50'])
                sl = lowest_sma - data.sl_const
                base = balance / entry_price
                base -= base * TAKER_FEE_RATE
                m_data['data'][str(row['timestamp'])] = {'side': 'buy', 'close': round(row['close'], 2), 'balance': round(base, 5)}

        elif pos and ( ( (row['sell_signal'] == 1 and (row['sma_20'] < row['sma_50'])) if use_close else (row['high'] >= tp or row['low'] <= sl) )):
            pos= False
            cnt += 1
            exit_price = row['close'] if use_close else (tp if row['high'] >= tp else sl) 
            new_balance = base * exit_price
            new_balance -= new_balance * MAKER_FEE_RATE
            profit =  new_balance - balance
            profit = round(profit, 2)
            profit_percent = (exit_price - entry_price) / entry_price * 100
            profit_percent = round(profit_percent, 2)
            new_balance= round(new_balance, 2)
            balance = start_bal + profit
            start_bal = balance
            if profit < 0:
                 loss += 1
            else:
                gain += 1
            m_data['data'][str(row['timestamp'])] = {'side': 'sell', 'close': round(row['close'], 2), 'balance': new_balance, 'profit': f"{profit}\t{profit_percent}%"}

    print(f"TOTAL TRADES: {cnt}")

    gain = round(gain * 100 / cnt, 2)
    loss = round(loss * 100 / cnt, 2)
    m_data = {**m_data, 'balance': round(balance / lev, 2), 'trades': cnt, "gain": gain, 'loss': loss }
    return  m_data
