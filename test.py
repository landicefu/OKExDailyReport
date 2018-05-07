#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

from OKExAPI.REST_V1 import OkcoinSpotAPI
from OKExAPI.Web import Api
from OKExAPI.Common import ApiCredential
from datetime import datetime

OKEX_BASE_URL = 'www.okex.com'

login_credential = Api.LoginCredential.load_from_file('.login_secret.json')
api_credential = ApiCredential.load_from_file('.secret.json')
spot = OkcoinSpotAPI.OKCoinSpot(OKEX_BASE_URL, api_credential)
token = Api.get_token(login_credential)

# gc = gspread.authorize(credentials)
# sps = gc.open('Test Spreadsheet')
# spreadsheet = gc.create('Test Spreadsheet')
# spreadsheet.add_worksheet('work1', 1, 10)
# spreadsheet.share('rusty.flower@gmail.com', perm_type='user', role='writer')
