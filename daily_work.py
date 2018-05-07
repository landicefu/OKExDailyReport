from OKExAPI.Common import ApiCredential
from OKExAPI import Web
from OKExAPI.REST_V1 import OkcoinSpotAPI
import ExchangeRateApi
import Util

from oauth2client.service_account import ServiceAccountCredentials

from AccountInfo import AccountInfo

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
google_credential = ServiceAccountCredentials.from_json_keyfile_name('.google_service_account_secret.json', scope)


OKEX_BASE_URL = 'www.okex.com'
EXCHANGE_API_TOKEN = open('.exchange_api_token', 'r').read().strip()
TARGET_CURRENCY = 'TWD'


def process():
    login_credential = Web.Api.LoginCredential.load_from_file('.login_secret.json')
    api_credential = ApiCredential.load_from_file('.secret.json')
    token = Web.Api.get_token(login_credential)
    spot = OkcoinSpotAPI.OKCoinSpot(OKEX_BASE_URL, api_credential)
    balance = Web.Api.user_balance(token)
    btc_usdt_price = spot.ticker('btc_usdt')['ticker']['last']
    usd_target_price = ExchangeRateApi.get_exchange_rate(Util.read_all('.exchange_api_token'), 'usd', TARGET_CURRENCY)
    unsettled_trades = Web.Api.user_unsettled_trades(token)

    user_info = AccountInfo(
        balance, btc_usdt_price, usd_target_price, TARGET_CURRENCY,
        unsettled_trades
    )

    for unsettled_trade in user_info.unsettled_trades:
        print('trade %f %s for %f %s' % (
            unsettled_trade.loss_amount_estimate(), unsettled_trade.loss_currency(),
            unsettled_trade.gain_amount_estimate(), unsettled_trade.gain_currency()
        ))


if __name__ == '__main__':
    process()
