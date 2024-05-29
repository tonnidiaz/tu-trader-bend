from flask_apscheduler import APScheduler

MAKER_FEE_RATE = .1/100
TAKER_FEE_RATE = .08/100
klines_dir =  'data/klines/binance'
dfs_dir = 'data/dfs/binance'
details = {
    'title': 'TuTrader',
    'admin_email': 'tunedstreamz@gmail.com',
    'developer': {'email': 'tunedstreamz@gmail.com'}
}

scheduler = APScheduler()