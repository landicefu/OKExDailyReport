import json
from OKExAPI.Common import ApiCredential
from OKExAPI import Web
from OKExAPI.REST_V1 import OkcoinSpotAPI

OKEX_BASE_URL = 'www.okex.com'
BTC_SKIP_THRESHOLD = 0.00001


def over_threshold(balance_data):
    valuation = float(balance_data['valuation'])
    return valuation >= BTC_SKIP_THRESHOLD


def process():
    login_credential = Web.Api.LoginCredential.load_from_file('.login_secret.json')
    api_credential = ApiCredential.load_from_file('.secret.json')
    token = Web.Api.get_token(login_credential)
    spot = OkcoinSpotAPI.OKCoinSpot(OKEX_BASE_URL, api_credential)

    balances = Web.Api.user_balance(token)['data']['balance']
    total_value_btc = 0
    for balance_data in balances:
        if over_threshold(balance_data):
            currency = balance_data['currency']
            valuation = float(balance_data['valuation'])
            total_value_btc += valuation
            print(
                "%s - %f" % (
                    currency,
                    valuation
                )
            )
    btc_value_usdt = float(spot.ticker('btc_usdt')['ticker']['last'])
    print("Total %f in BTC ; %f in USDT" % (total_value_btc, btc_value_usdt * total_value_btc))


if __name__ == '__main__':
    process()


