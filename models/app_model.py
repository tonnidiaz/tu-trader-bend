from bunnet import Document

class App(Document):
    can_trade: bool = True
    use_swing_low: bool = True
    base: str = 'ETH'
    ccy: str = 'USDT'
    p_gain: float = 1/100
    sl_const: float = 30
    strict: bool = False
    demo: bool = True
    interval:int = 15
    category: str = 'spot'
    mult: float = 1.8
    ce_length: int = 1