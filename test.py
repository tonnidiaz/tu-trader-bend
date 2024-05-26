from datetime import datetime
import os
from utils.functions import heikin_ashi, parse_klines
from utils.constants import dfs_dir
import pandas as pd

symb = "ETHUSDT"
interval = 15
start = "2021-05-10 00:00:00"
end = "2021-05-20 23:59:00"

def main():
    
    d = datetime.now()
    print(d)

main()