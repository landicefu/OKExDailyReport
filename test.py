#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

from OKExAPI.REST_V1 import OkcoinSpotAPI
from OKExAPI.Web.LoginCredential import LoginCredential
from OKExAPI.Web import Api
from OKExAPI.Common import ApiCredential


OKEX_BASE_URL = 'www.okex.com'

login_credential = LoginCredential.load_from_file('.login_secret.json')
api_credential = ApiCredential.load_from_file('.secret.json')
token = Api.get_token(login_credential)

spot = OkcoinSpotAPI.OKCoinSpot(OKEX_BASE_URL, api_credential)
print(spot.kLine('btc_usdt', '1day'))
