import pandas as pd
from data.data import data
from strategies.funcs import strategy

class Strategy:
    name: str
    desc: str = ""

    def buy_cond(self):
        return
    
    def sell_cond(self, row: pd.Series, entry: float):
        return
    
    def run(self, df: pd.DataFrame, balance: float, lev=1, p_gain=None):
        print(f"\nRunning {self.name} strategy [{self.desc}]\n")
        m_data = strategy(df, balance, self.buy_cond,
                          self.sell_cond, lev, p_gain if p_gain else data.p_gain)
        return m_data
        