from datetime import datetime
from classes.OKX import OKX
from models.order_model import Order

def update_order(orders: list[Order]):

    is_closed = True
    last_order = None
    okx : OKX = OKX.inst
    if len(orders) and not orders[-1].is_closed:
        last_order = orders[-1]
        print(f"LAST_ORDER: {last_order}\n")
        is_closed = last_order.is_closed
        oid = last_order.order_id if last_order.side == 'sell' else last_order.buy_order_id
        res = okx.get_order_by_id(oid)
        
        if res is None:
            return None
        _is_closed = res["state"] != "live"

        if last_order.side == "sell":
            print("Last order side is sell\n")
            
            if _is_closed:
                
                last_order.sell_price = float(res["fillPx"])
                last_order.is_closed = _is_closed
                last_order.sell_fee = float(res["fee"])

                bal = last_order.base_amt * last_order.sell_price
                print(f'\nNEW_BALANCE: {bal}\n')

                profit = (
                    bal - last_order.ccy_amt
                ) / last_order.ccy_amt * 100
                last_order.profit = profit
                is_closed = _is_closed
            print('')

        else:
            print("Last order side is buy\n")
        
            if _is_closed:
                last_order.buy_price = float(res["fillPx"])
                last_order.buy_fee = float(res["fee"])
                last_order.base_amt = float(res["fillSz"])
                last_order.side = "sell"

        last_order.save()

    return is_closed, last_order