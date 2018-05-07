from datetime import datetime
from OKExAPI.Common import ApiCredential
from OKExAPI import Web
from OKExAPI.REST_V1 import OkcoinSpotAPI
import ExchangeRateApi
import Util

from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread import Spreadsheet, SpreadsheetNotFound, WorksheetNotFound

from AccountInfo import AccountInfo

GOOGLE_API_SCOPE = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
GOOGLE_CREDENTIAL = ServiceAccountCredentials.from_json_keyfile_name(
    '.google_service_account_secret.json', GOOGLE_API_SCOPE)
OKEX_BASE_URL = 'www.okex.com'
EXCHANGE_API_TOKEN = open('.exchange_api_token', 'r').read().strip()

TARGET_CURRENCY = 'TWD'
GS_SHEET_TITLE = 'OKEX Daily Report'
USER_EMAIL = 'rusty.flower@gmail.com'

COLUMN_NAMES_BALANCE = [
    'Currency',
    'Available',
    'On Hold',
    'BTC Value',
    'USDT Value',
    TARGET_CURRENCY + ' Value',
    'USDT Avg Price',
    'USDT Current Price',
    'USDT Profit',
    'TWD Profit',
    'Percentage Profit'
]
COLUMN_NAMES_UNSETTLE = [
    'Create',
    'Pair',
    'Action',
    'Volume',
    'Filled',
    'Price',
    'Avg. Price',
    'Estimated Fee'
    'Will Gain',
    'Will Loss',
    'USDT Current Value',
    'USDT Target Value',
    'Target Percentage Diff'
]
COLUMN_NAMES_TRADE_HISTORY = [
    'Time',
    'Buy Token',
    'Sell Token',
    'Price',
    'Amount',
    'Balance',
    'USDT fee',
    'buy_id',
    'sell_id'
]


def create_worksheet(spreadsheet: Spreadsheet, title: str, num_row: int, num_col: int):
    print('Creating worksheet %s [%d, %d]' % (title, num_row, num_col))
    spreadsheet.add_worksheet(title, num_row, num_col)


def create_google_spreadsheet(gc: gspread.Client) -> Spreadsheet:
    print('Creating spreadsheet')
    spreadsheet = gc.create(GS_SHEET_TITLE)
    create_worksheet(spreadsheet, 'Summary', 10, 10)
    create_worksheet(spreadsheet, 'Balance', 1, len(COLUMN_NAMES_BALANCE))
    create_worksheet(spreadsheet, 'Unsettled Trades', 1, len(COLUMN_NAMES_UNSETTLE))
    create_worksheet(spreadsheet, 'Trade History', 1, len(COLUMN_NAMES_TRADE_HISTORY))
    default_worksheet = spreadsheet.get_worksheet(0)
    spreadsheet.del_worksheet(default_worksheet)
    spreadsheet.share(USER_EMAIL, 'user', 'writer', True, 'This is your new OKEX daily report')
    print('Spreadsheet was shared to user ' + USER_EMAIL)
    return spreadsheet


def delete_all_spreadsheet():
    gc = gspread.authorize(GOOGLE_CREDENTIAL)
    spreadsheets = gc.openall(GS_SHEET_TITLE)
    print('Deleting %d spreadsheets' % len(spreadsheets))
    for spreadsheet in spreadsheets:
        gc.del_spreadsheet(spreadsheet.id)


def init_google_spreadsheet() -> Spreadsheet:
    gc = gspread.authorize(GOOGLE_CREDENTIAL)
    try:
        spreadsheet = gc.open(GS_SHEET_TITLE)
    except SpreadsheetNotFound:
        print('Google Spreadsheet with title \'%s\' is not found' % GS_SHEET_TITLE)
        spreadsheet = create_google_spreadsheet(gc)
    return spreadsheet


def process():
    init_google_spreadsheet()
    login_credential = Web.Api.LoginCredential.load_from_file('.login_secret.json')
    api_credential = ApiCredential.load_from_file('.secret.json')
    token = Web.Api.get_token(login_credential)
    spot = OkcoinSpotAPI.OKCoinSpot(OKEX_BASE_URL, api_credential)
    balance = Web.Api.user_balance(token)
    btc_usdt_price = spot.ticker('btc_usdt')['ticker']['last']
    if TARGET_CURRENCY.lower() == 'usd':
        usd_target_price = 1
    else:
        usd_target_price = ExchangeRateApi.get_exchange_rate(Util.read_all('.exchange_api_token'), 'usd', TARGET_CURRENCY)
    unsettled_trades = Web.Api.user_unsettled_trades(token)

    user_info = AccountInfo(
        balance, btc_usdt_price, usd_target_price, TARGET_CURRENCY,
        unsettled_trades
    )

    for unsettled_trade in user_info.unsettled_trades:
        print('Trade %f %s for %f %s' % (
            unsettled_trade.loss_amount_estimate(), unsettled_trade.loss_currency(),
            unsettled_trade.gain_amount_estimate(), unsettled_trade.gain_currency()
        ))


if __name__ == '__main__':
    process()
