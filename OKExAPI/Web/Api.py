#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Dict, Tuple

import requests
import os
import json
import uuid
from datetime import datetime

from AccountInfo import Balance


class LoginCredential:

    def __init__(self, area_code: str, login_name: str, password: str):
        self.area_code = area_code
        self.login_name = login_name
        self.password = password

    @staticmethod
    def load_from_file(file_path):
        json_data = json.loads(open(file_path, 'r').read())
        return LoginCredential(
            json_data['areaCode'],
            json_data['loginName'],
            json_data['password']
        )


def login_step2(device_id: str, token: str, step_code: str, step2type: str):
    headers = {
        'devid': device_id,
        'referer': 'https://www.okex.com/account/login',
        'authorization': token,
    }

    params = (
        ('stepCode', step_code),
        ('step2Type', step2type),
    )
    response = requests.get('https://www.okex.com/v3/users/login-auth/login-step2', headers=headers, params=params).json()
    return response


def get_uuid():
    if os.path.isfile('.uuid'):
        with open('.uuid', 'r') as file:
            device_uuid = file.read().strip()
        return device_uuid
    device_uuid = str(uuid.uuid1())
    with open('.uuid', 'w') as file:
        print(device_uuid, file=file)
    return device_uuid


def login(login_credential: LoginCredential, save_cache: bool = True) -> str:
    print('Login starts')
    device_id = get_uuid()
    headers = {
        'loginname': login_credential.login_name,
        'devid': device_id,
        'referer': 'https://www.okex.com/account/login?forward=/spot/trade',
    }

    params = (
        ('loginName', login_credential.login_name),
    )

    data = {
        "areaCode": login_credential.area_code,
        "loginName": login_credential.login_name,
        "password": login_credential.password
    }

    response = requests.post('https://www.okex.com/v3/users/login/login', headers=headers, params=params, data=str(data)).json()
    token = response['data']['token']
    if 'step2Type' in response['data'].keys():
        print('Need to do step 2 verification')
        step2type = response['data']['step2Type']
        if step2type == 1:
            print('Google Authentication Code: ', end='')
            step2code = input()
        response = login_step2(device_id, token, step2code, step2type)
        token = response['data']['token']

    if save_cache:
        with open(".cached_token", "w") as cache_file:
            print(json.dumps(response), file=cache_file)
    return token


def get_cached_token() -> str:
    cached_token_path = '.cached_token'
    if os.path.isfile(cached_token_path):
        with open(cached_token_path, 'r') as file:
            text = file.read()
        token_json = json.loads(text)
        due = datetime.fromtimestamp(token_json['data']['pastDue']/1000)
        if (due - datetime.now()).total_seconds() > 60 * 30:
            token = token_json['data']['token']
            return token
        else:
            print('The cache token was expired')
    return None


def get_token(login_credential: LoginCredential) -> str:
    cached_token = get_cached_token()
    if cached_token:
        return cached_token
    return login(login_credential)


def get_currencies():
    headers = {
        'referer': 'https://www.okex.com/marketList',
        'x-requested-with': 'XMLHttpRequest',
    }

    response = requests.get('https://www.okex.com/v2/spot/markets/currencies', headers=headers)
    return response.json()


def get_products():
    headers = {
        'referer': 'https://www.okex.com/marketList',
        'x-requested-with': 'XMLHttpRequest',
    }

    response = requests.get('https://www.okex.com/v2/spot/markets/products', headers=headers)
    return response.json()


class Bill:
    def __init__(self, json_data):
        self.type = int(json_data['type'])
        self.size = float(json_data['size'])
        self.currency = json_data['currency']
        self.price = float(json_data['price'])


def bill_types(token: str) -> Dict[int, Tuple[str, str]]:
    headers = {
        'authorization': token,
        'referer': 'https://www.okex.com/account/balance/accountRecords',
    }
    types = requests.get('https://www.okex.com/v2/spot/bills/types', headers=headers).json()['data']
    type_dict = {}
    for type_item in types:
        type_dict[type_item['code']] = (type_item['type'], type_item['desc'])
    return type_dict


def user_bills(token: str,
               currency_id: int = -1,
               begin_date: int = 0,
               end_date: int = 0,
               is_history: bool = False,
               page: int = 1,
               per_page: int = 300,
               record_type: int = 0) -> List[Bill]:

    headers = {
        'authorization': token,
        'referer': 'https://www.okex.com/account/balance/accountRecords'
    }

    data = {
        "currencyId": currency_id,
        "recordType": record_type,
        "beginDate": begin_date,
        "endDate": end_date,
        "isHistory": str(is_history).lower(),
        "page": {
            "page": page,
            "perPage": per_page
        }
    }
    response = requests.post('https://www.okex.com/v2/spot/bills/bills', headers=headers, data=str(data))
    bill_array = response.json()['data']['billList']
    bills = []  # type: list[Bill]

    for bill in bill_array:
        bills.append(Bill(bill))
    return bills


def user_balance(token: str):
    headers = {
        'authorization': token,
        'referer': 'https://www.okex.com/account/balance',
    }

    params = (
        ('transferFrom', '1'),
    )

    response = requests.get(
        'https://www.okex.com/v2/asset/accounts/user-currency-balance',
        headers=headers,
        params=params
    )
    return response.json()


def user_unsettled_trades(token: str):
    headers = {
        'authorization': token,
        'referer': 'https://www.okex.com/spot/trade',
    }

    params = (
        ('symbol', 'all'),
        ('systemType', '1'),
        ('page', '1'),
        ('perSize', '20'),
    )

    response = requests.get('https://www.okex.com/v2/spot/order/unsettlement', headers=headers, params=params)
    return response.json()


def user_history_trades(
        token: str, symbol: str, page: int = 1, per_page: int = 20,
        start_millis: int = 0, end_millis: int = int(datetime.now().timestamp() * 1000)):

    headers = {
        'authorization': token,
        'referer': 'https://www.okex.com/spot/orders',
    }

    params = (
        ('page', page),
        ('perPage', per_page),
        ('systemType', '-1'),
        ('symbol', symbol),
        ('entrustType', 'history'),
        ('startDateMillis', start_millis),
        ('endDateMillis', end_millis),
    )

    response = requests.get('https://www.okex.com/v2/spot/order/history', headers=headers, params=params)
    return response.json()
