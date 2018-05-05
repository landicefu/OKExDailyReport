#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

from OKExAPI.REST_V1.OkcoinSpotAPI import OKCoinSpot
from OKExAPI.Common import *


OKEx_BASE_URL = 'www.okex.com'
credential = Credential.load_from_file('.secret.json')

spot = OKCoinSpot(OKEx_BASE_URL, credential)
print(spot.userinfo())
