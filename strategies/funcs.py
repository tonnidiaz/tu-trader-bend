from data.data import data
from utils.constants import MAKER_FEE_RATE, TAKER_FEE_RATE
import pandas as pd

def bal_profit_calculator(start_bal: float, balance: float, base: float, entry_price: float, exit_price: float, fee: float, data, row):
    """ Returns start_bal, balance, profit """
    new_balance = base * exit_price
    new_balance -= new_balance * fee
    profit = new_balance - balance
    profit = round(profit, 2)
    profit_percent = (exit_price - entry_price) / entry_price * 100
    profit_percent = round(profit_percent, 2)
    new_balance = round(new_balance, 2)
    balance = start_bal + profit
    start_bal = balance

    data['data'][str(row['timestamp'])] = {'side': 'sell', 'close': round(
        row['close'], 2), 'balance': new_balance, 'profit': f"{profit}\t{profit_percent}%"}

    return start_bal, balance, profit, data

def strategy(df: pd.DataFrame, balance: float, buy_cond, sell_cond, lev=1, p_gain=None, use_close = True):

    pos = False
    cnt = 0
    gain, loss = 0, 0
    p_gain = p_gain if p_gain else data.p_gain
    start_bal = balance

    m_data = {'data': {}}
    print("CE_SMA: BEGIN BACKTESTING...\n")
    for i, row in df.iterrows():

        if not pos and buy_cond(row):
            pos = True
            balance *= lev
            entry_price = row['close']
            tp = entry_price * (1 + p_gain)
            lowest_sma = min(row['sma_20'], row['sma_50'])
            sl = lowest_sma - data.sl_const
            base = balance / entry_price
            base -= base * TAKER_FEE_RATE
            m_data['data'][str(row['timestamp'])] = {'side': 'buy', 'close': round(
                row['close'], 2), 'balance': round(base, 5)}

        elif pos and sell_cond(row, tp, sl):
            pos = False
            cnt += 1
            exit_price = row['close'] if use_close else (tp if row['high'] >= tp else sl)

            start_bal, balance, profit, _data = bal_profit_calculator(
                start_bal, balance, base, entry_price, exit_price, MAKER_FEE_RATE, m_data, row)

            if profit < 0:
                loss += 1
            else:
                gain += 1

            m_data = _data

    print(f"TOTAL TRADES: {cnt}")
    cnt = cnt if cnt > 0 else 1
    gain = round(gain * 100 / cnt, 2)
    loss = round(loss * 100 / cnt, 2)
    m_data = {**m_data, 'balance': round(balance / lev, 2),
              'trades': cnt, "gain": gain, 'loss': loss}
    return m_data
