from datetime import datetime
import json
from dotenv import load_dotenv
from flask import Flask, request
from classes.OKX import OKX
from classes.binance import Binance
from models.app_model import App
from models.user_model import User
from routes.backtest import router as backtest_bp
from routes.auth import router as auth_bp
from flask_cors import CORS
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO
from utils.functions import chandelier_exit, get_app, heikin_ashi, is_dev, parse_klines
from utils.functions2 import update_order
from utils.io.functions import on_backtest
from utils.mongo import TuMongo
from utils.io.io import socketio
import gunicorn
from models.order_model import Order
from models.app_model import App
from strategies.main import strategies

load_dotenv()
g = gunicorn
# Init mongo
TuMongo()

def init():

    # Create app if not present
    apps = App.find().run()
    if not len(apps):
        # Creating new app
        App().save()
    else:
        print(apps[0])
    OKX.inst = OKX()
    Binance.inst = Binance()
    
app = Flask(__name__)

CORS(app, origins="*")

class Config:
    SCHEDULER_API_ENABLED = True
app.config.from_object(Config)


socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

@socketio.on('connect')
def test_connect(msg):
    print(f'Connected: {msg}')
    return
    if msg:
        uname = msg.get('username')
        user = User.find_one(User.username == uname).run()
        if not user:
            raise ConnectionRefusedError("Unauthorised")

        print(request.sid)
        user.io_id = request.sid
        user.save()
        print("USER IO ID UPDATED")
        


@socketio.on('disconnect')
def test_disconnect(msg):
    print('Client disconnected: ', msg)

@socketio.on('backtest')
def _on_backtest(data):
    print('\nON BACKTEST\n')
    on_backtest(data)

scheduler = APScheduler()
init()

app.register_blueprint(backtest_bp)
app.register_blueprint(auth_bp)

cnt = 0

def place_trade(amt: float | None = None, ts=None, price: float = 0, side="buy"):

    _app = get_app()
    orders = Order.find().run()
    okx : OKX = OKX.inst

    if amt is None:
        # GET THE USDT BALANCE AND USE 75 IF THIS IS FIRST ORDER
        print('\nFIRST ORDER\n')
        amt = okx.get_bal(ccy=_app.ccy)
    print(f"Avail amt: {amt}\n")

    if not amt:
        raise Exception("Amount not avail")

    # Trade half assets
    if side == "buy":
        if len(orders) == 0:
            amt = 75 if amt > 75 else amt
        else:
            last_order = orders[-1]
            amt = last_order.ccy_amt * (1 + last_order.profit / 100)

    else:
        # Sell all previously traded
        amt = orders[-1].base_amt

    print(f"PLACING A {side} order FOR [{amt}]\n")
    order_id = okx.place_order(amt, side=side, price=price)

    if not order_id:
        print("FAILED TO PLACE ORDER")
        return
    m_order = okx.get_order_by_id(order_id=order_id)

    # Save order
    if side == "buy":
        order = Order(
            buy_order_id=order_id,
            buy_price=price,
            buy_timestamp=str(ts),
            buy_fee=float(m_order["fee"]),
            ccy_amt=amt,
            side=side,
        )
    else:
        order = orders[-1]
        order.order_id = order_id
        order.sell_timestamp = str(ts)
        order.sell_fee = float(m_order["fee"])
        order.sell_price = price
        order.base_amt = amt
        order.side = side

    order.save()

    print("DB UPDATED\n")


TIME_CHECKER_JOB_ID = "TIME_CHECKER_JOB"

last_check_at: datetime | None = None
test = False



def check_n_place_orders():

    global cnt, last_check_at
    okx : OKX= OKX.inst
    binance : Binance= Binance.inst
    now = datetime.now()
    curr_min = now.minute
    app = get_app()
    m_test = test and len(Order.find().run()) <= 1
    if test:
        print(f"CURR_MIN: [{curr_min}]\tTEST: {m_test}\n")

    prod_time_condition = (
        app.can_trade
        and curr_min % app.interval == 0
        and (
            f"{last_check_at.hour}:{last_check_at.minute}"
            != f"{now.hour}:{now.minute}"
            if last_check_at
            else True
        )
    )

    if m_test or prod_time_condition:
        last_check_at = datetime.now()
        scheduler.pause_job(TIME_CHECKER_JOB_ID)
        # Check orders
        orders = Order.find().run()
        is_closed, last_order = update_order(orders)

        klines = binance.get_klines(symbol=f"{app.base}{app.ccy}")
        df = chandelier_exit(heikin_ashi(parse_klines(klines)))


        if is_dev():
            df.to_csv("data/df.csv")
            print("DF SAVED TO CSV FILE")

        print("CHECKING SIGNALS...\n")

        for i, row in df.tail(1).iterrows():
            obj = {'ts': row['timestamp'], 'buy_signal' : row['buy_signal'], 'sell_signal': row["sell_signal"], 'sma_20': row['sma_20'], 'sma_50': row['sma_50']}
            print(f'\n{obj}\n')
            if  is_closed and (
                row["buy_signal"] == 1 and (row["sma_20"] > row["sma_50"]) or m_test
            ):

                print(f"HAS BUY SIGNAL > GOING IN: {last_order}")
                amt = last_order.ccy_amt * (1 +  last_order.ccy_amt * last_order.profit / 100) if last_order is not None else None
                place_trade(ts=row["timestamp"], amt=amt)

            elif not is_closed and last_order.side == 'sell' and last_order.order_id == '':
                
                entry = last_order.buy_price
                if  strategies[app.strategy - 1].sell_cond(row, entry) or m_test:
                    print("HAS SELL SIGNAL > GOING OUT")
                    amt = last_order.base_amt
                    place_trade(ts=row["timestamp"], price=row["close"], side="sell", amt=amt)
                    
        print("RESUME JOB")
        scheduler.resume_job(TIME_CHECKER_JOB_ID)

@scheduler.task("interval", id=TIME_CHECKER_JOB_ID, seconds=1, misfire_grace_time=900)
def tc_job():

    with scheduler.app.app_context():
        global cnt
        check_n_place_orders()
        cnt += 1

scheduler.app = app
scheduler.init_app(app)


@app.get("/")
def index_route():
    return 'OHK'

@app.get("/orders")
def orders_route():
    orders: list[Order] = Order.find().run()
    orders = list(map(lambda x: json.loads(x.model_dump_json()), orders))
    return orders

@app.get('/strategies')
def strategies_route():
    data = list(map(lambda x: vars(x), strategies))
    return data

scheduler.start()
#socketio.run(app, allow_unsafe_werkzeug=True)
if __name__ == '__main__':
    socketio.run(app, debug=False, port=8000)
    