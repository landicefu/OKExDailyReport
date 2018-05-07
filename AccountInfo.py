BTC_VALUATION_SKIP_THRESHOLD = 0.00001


def over_threshold(balance_data):
    valuation = float(balance_data['valuation'])
    return valuation >= BTC_VALUATION_SKIP_THRESHOLD


class Balance:
    def __init__(self, currency: str, balance: float, hold: float, valuation: float):
        self.currency = currency
        self.balance = balance
        self.hold = hold
        self.valuation = valuation

    @classmethod
    def from_json(cls, json_balance):
        return cls(
            json_balance['currency'],
            float(json_balance['balance']),
            float(json_balance['hold']),
            float(json_balance['valuation']))


class SpotTrades:
    def __init__(self, order_id: str, create_time: int, order_type: int, system_type: int,
                 symbol: str, product_id: int, side: int,
                 size: float, filled_size: float, not_strike: float, price: float,
                 status: int):
        self.order_id = order_id
        self.create_time = create_time
        self.order_type = order_type    # type 0 = spot
        self.system_type = system_type
        self.symbol = symbol
        self.product_id = product_id
        self.side = side                # side 1 = buy ; side 2 = sell
        self.size = size                # total volume to trade
        self.filled_size = filled_size  # part already fulfilled
        self.not_strike = not_strike    # part not fulfilled
        self.price = price              # target price
        self.status = status            # status 0 = open

    @classmethod
    def from_json(cls, json_data):
        return cls(int(json_data['id']), int(json_data['createTime']), int(json_data['orderType']),
                   int(json_data['systemType']), json_data['symbol'], int(json_data['productId']),
                   int(json_data['side']), float(json_data['size']), float(json_data['filledSize']),
                   float(json_data['notStrike']), float(json_data['price']), int(json_data['status']))

    def gain_currency(self):
        split = self.symbol.split('_')
        if self.side == 1:
            return split[0]
        else:
            return split[1]

    def loss_currency(self):
        split = self.symbol.split('_')
        if self.side == 1:
            return split[1]
        else:
            return split[0]

    def gain_amount_estimate(self):
        if self.side == 1:
            return self.size
        else:
            return self.size * self.price

    def loss_amount_estimate(self):
        if self.side == 1:
            return self.size * self.price
        else:
            return self.size


class AccountInfo:
    def __init__(self, balance_resp, btc_usdt_price: float, usd_target_price: float, target_currency: str,
                 unsettled_trades):
        self.btc_usdt_price = btc_usdt_price
        self.usd_target_price = usd_target_price
        self.target_currency = target_currency
        self.balances = []  # type: list[Balance]
        self.unsettled_trades = []  # type: list[SpotTrades]
        for balance in balance_resp['data']['balance']:
            if over_threshold(balance):
                self.balances.append(Balance.from_json(balance))
        for unsettled_trade in unsettled_trades['data']['orders']:
            self.unsettled_trades.append(SpotTrades.from_json(unsettled_trade))
