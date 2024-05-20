import json
from utils.functions import heikin_ashi, parse_klines

fp = 'data/klines/binance/klines.json'

with open(fp) as f:
    klines = json.load(f)

df = heikin_ashi(parse_klines(klines))
df.to_csv('data/dfs/binance/df.csv')
print('DONE')