import json
from flask import Blueprint, request
import pandas as pd
from classes.binance import Binance
from utils.functions import chandelier_exit, date_str_to_timestamp, err_handler, heikin_ashi, parse_klines, tu_path
from utils.constants import dfs_dir
router = Blueprint('backtest', __name__)

test = False

@router.post('/backtest')
def backtest_route():
    body = request.json
    str_num = int(body.get('strategy'))
    df = pd.read_csv(tu_path(f'{dfs_dir}/df.csv'))
    bal = float(body.get('bal'))
    #return ce_sma_strategies(df, bal, str_num)
