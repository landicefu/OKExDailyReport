from typing import List
from datetime import datetime

from OKExAPI.Common import ApiCredential
from OKExAPI import Web
from OKExAPI.REST_V1 import OkcoinSpotAPI
import ExchangeRateApi
import Util

from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread import Spreadsheet, SpreadsheetNotFound, Worksheet, WorksheetNotFound, Cell

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

COLUMNS_NAMES_HISTORY_VALUATION = [
    'DATE',
    'USD',
    'TWD'
]
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
    TARGET_CURRENCY + ' Profit',
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
    return spreadsheet.add_worksheet(title, num_row, num_col)


def create_google_spreadsheet(gc: gspread.Client) -> Spreadsheet:
    print('Creating spreadsheet')
    spreadsheet = gc.create(GS_SHEET_TITLE)
    balance_worksheet = create_worksheet(spreadsheet, 'Summary', 0, 0)
    balance_worksheet.append_row([
        'USD', TARGET_CURRENCY
    ])

    worksheet = create_worksheet(spreadsheet, 'History Valuation', 1, len(COLUMNS_NAMES_HISTORY_VALUATION))
    worksheet.append_row(COLUMNS_NAMES_HISTORY_VALUATION)

    worksheet = create_worksheet(spreadsheet, 'Balance', 1, len(COLUMN_NAMES_BALANCE))
    worksheet.insert_row(COLUMN_NAMES_BALANCE, 1)
    balance_worksheet.update_cell(2, 1, '=SUM(Balance!E:E)')
    balance_worksheet.update_cell(2, 2, '=SUM(Balance!F:F)')

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


def get_account_info(token: str, spot: OkcoinSpotAPI.OKCoinSpot) -> AccountInfo:
    balance = Web.Api.user_balance(token)
    btc_usdt_ticker = spot.ticker('btc_usdt')
    current_time = datetime.fromtimestamp(int(btc_usdt_ticker['date']))
    btc_usdt_price = float(btc_usdt_ticker['ticker']['last'])
    if TARGET_CURRENCY.lower() == 'usd':
        usd_target_price = 1
    else:
        usd_target_price = ExchangeRateApi.get_exchange_rate(Util.read_all('.exchange_api_token'), 'usd',
                                                             TARGET_CURRENCY)
    unsettled_trades = Web.Api.user_unsettled_trades(token)

    account_info = AccountInfo(
        current_time,
        balance, btc_usdt_price, usd_target_price, TARGET_CURRENCY,
        unsettled_trades
    )
    return account_info


def get_worksheet_by_title(worksheets: List[Worksheet], title: str) -> Worksheet:
    for worksheet in worksheets:
        if worksheet.title == title:
            return worksheet
    raise WorksheetNotFound('Worksheet with title ' + title + ' was not found')


def write_latest_info(spreadsheet: Spreadsheet, account_info: AccountInfo):
    worksheets = spreadsheet.worksheets()
    history_valuation_worksheet = get_worksheet_by_title(worksheets, 'History Valuation')
    balance_worksheet = get_worksheet_by_title(worksheets, 'Balance')
    balance_worksheet.resize(1, len(COLUMN_NAMES_BALANCE))

    total_usd_valuation = 0
    total_target_valuation = 0
    for balance in account_info.balances:
        usd_valuation = balance.valuation * account_info.btc_usdt_price
        total_usd_valuation += usd_valuation
        target_valuation = usd_valuation * account_info.usd_target_price
        total_target_valuation += target_valuation
        if balance.currency.lower() == 'usdt':
            average_usd_price = 1
            current_usd_price = 1
        else:
            average_usd_price = 1  #
            current_usd_price = 1.3  #
        usd_profit = (current_usd_price - average_usd_price) * usd_valuation
        target_currency_profit = usd_profit * account_info.usd_target_price
        print('Insert %s balance %s %f' % (balance.currency, account_info.target_currency, target_valuation))
        balance_worksheet.append_row([
            balance.currency,
            balance.balance,
            balance.hold,
            balance.valuation,
            usd_valuation,
            target_valuation,
            average_usd_price,
            current_usd_price,
            usd_profit,
            target_currency_profit,
            (current_usd_price - average_usd_price) / average_usd_price * 100
        ])
    date_str = account_info.get_date_str()
    if date_str == history_valuation_worksheet.cell(history_valuation_worksheet.row_count, 1).value:
        row = history_valuation_worksheet.row_count  # update
        cells = [Cell(row, 1, date_str), Cell(row, 2, total_usd_valuation), Cell(row, 3, total_target_valuation), ]
        history_valuation_worksheet.update_cells(cells)
    else:
        history_valuation_worksheet.append_row([date_str, total_usd_valuation, total_target_valuation])


def process():
    # delete_all_spreadsheet()
    spreadsheet = init_google_spreadsheet()
    login_credential = Web.Api.LoginCredential.load_from_file('.login_secret.json')
    api_credential = ApiCredential.load_from_file('.secret.json')
    token = Web.Api.get_token(login_credential)
    spot = OkcoinSpotAPI.OKCoinSpot(OKEX_BASE_URL, api_credential)
    account_info = get_account_info(token, spot)
    write_latest_info(spreadsheet, account_info)


if __name__ == '__main__':
    process()
