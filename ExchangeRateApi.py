#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests

# https://www.exchangerate-api.com/


# get 1 currency1 value in currency2
def get_exchange_rate(api_token: str, currency1: str, currency2: str, amount_currency1: int = 1.0):
    resp = requests.get('https://v3.exchangerate-api.com/bulk/%s/%s' % (api_token, currency1.upper()))
    return float(resp.json()['rates'][currency2.upper()]) * amount_currency1
