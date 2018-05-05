#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

from OKExAPI.REST_V1 import OkcoinSpotAPI
from OKExAPI.Web import Api
from OKExAPI.Common import ApiCredential


OKEX_BASE_URL = 'www.okex.com'

login_credential = Api.LoginCredential.load_from_file('.login_secret.json')
api_credential = ApiCredential.load_from_file('.secret.json')
token = Api.get_token(login_credential)

print(Api.user_balance(token))
