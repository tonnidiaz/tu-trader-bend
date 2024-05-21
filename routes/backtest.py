import json
from flask import Blueprint, request

from classes.binance import Binance
from routes.strategies.ce_sma import ce_sma_backtest
from utils.functions import chandelier_exit, date_str_to_timestamp, err_handler, heikin_ashi, parse_klines

router = Blueprint('backtest', __name__)

test = False
