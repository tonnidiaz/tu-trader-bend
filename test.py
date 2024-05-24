import os
from utils.functions import heikin_ashi, parse_klines
from utils.constants import dfs_dir
import pandas as pd

symb = "ETHUSDT"
interval = 15
date = "2021-02-25 00:00:00 2021-03-30 23:59:00"
fp = 'data/klines/binance/klines.json'

def main():
    year = date.split('-')[0]
    fp = f"{dfs_dir}/{year}/{symb}_{interval}m.csv"
    if not os.path.exists(fp):
        return 'DataFrame does not exists'
    df = pd.read_csv(fp)
