import pandas as pd
from classes.strategy import Strategy
from strategies.funcs import strategy
from data.data import data


class Str_1(Strategy):
    
    def __init__(self):
        self.name = "Strategy 1"
        self.desc = "Exits on every sell signal "
    
    def buy_cond(self, row):
        return row['buy_signal'] == 1 and (row['sma_20'] is not None and row['sma_50'] is not None and row['sma_20'] > row['sma_50'])

    def sell_cond(self, row, tp, sl):
        return row['sell_signal'] == 1

    def run(self, df: pd.DataFrame, balance: float, lev=1, p_gain=None):
        super().run()
        m_data = strategy(df, balance, self.buy_cond,
                          self.sell_cond, lev, p_gain if p_gain else data.p_gain)
        return m_data


class Str_2(Strategy):
    
    def __init__(self):
        self.name = "Strategy 2"
        self.desc = """Exists when stop loss / take profit is reached """
    
    def buy_cond(self, row):
        return row['buy_signal'] == 1 and (row['sma_20'] is not None and row['sma_50'] is not None and row['sma_20'] > row['sma_50'])

    def sell_cond(self, row, tp, sl):
        return row['high'] >= tp or row['low'] <= sl

    def run(self, df: pd.DataFrame, balance: float, lev=1, p_gain=None):
        super().run()
        m_data = strategy(df, balance, self.buy_cond,
                          self.sell_cond, lev, p_gain if p_gain else data.p_gain)
        return m_data


class Str_3(Strategy):
    
    def __init__(self):
        self.name = "Strategy 3"
        self.desc = """Exists when SMA_20 > SMA_50"""
    
    def buy_cond(self, row):
        return row['buy_signal'] == 1 and (row['sma_20'] is not None and row['sma_50'] is not None and row['sma_20'] > row['sma_50'])

    def sell_cond(self, row, tp, sl):
        return row['sma_20'] < row['sma_50']

    def run(self, df: pd.DataFrame, balance: float, lev=1, p_gain=None):
        super().run()
        m_data = strategy(df, balance, self.buy_cond,
                          self.sell_cond, lev, p_gain if p_gain else data.p_gain)
        return m_data


class Str_4(Strategy):
    
    def __init__(self):
        self.name = "Strategy 4"
        self.desc = """Exists when SMA_20 > SMA_50 and also there is a sell signal """
    
    def buy_cond(self, row):
        return row['buy_signal'] == 1 and (row['sma_20'] is not None and row['sma_50'] is not None and row['sma_20'] > row['sma_50'])

    def sell_cond(self, row, tp, sl):
        return row['sell_signal'] and row['sma_20'] < row['sma_50']

    def run(self, df: pd.DataFrame, balance: float, lev=1, p_gain=None):
        super().run()
        m_data = strategy(df, balance, self.buy_cond,
                          self.sell_cond, lev, p_gain if p_gain else data.p_gain)
        return m_data


class Str_5(Strategy):
    
    def __init__(self):
        self.name = "Strategy 5"
        self.desc = """ Enters on every buy_signal and exits on every sell signal """
    
    def buy_cond(self, row):
        return row['buy_signal'] == 1

    def sell_cond(self, row, tp, sl):
        return row['sell_signal'] == 1

    def run(self, df: pd.DataFrame, balance: float, lev=1, p_gain=None):
        super().run()
        m_data = strategy(df, balance, self.buy_cond,
                          self.sell_cond, lev, p_gain if p_gain else data.p_gain)
        return m_data

strategies : list[Strategy] = [Str_1(), Str_2(), Str_3(), Str_4(), Str_5()]
