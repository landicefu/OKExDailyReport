#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

from OKExAPI.Web.Credential import Credential
from OKExAPI.Web import Api


OKEx_BASE_URL = 'www.okex.com'

credential = Credential.load_from_file('.login_secret.json')
token = Api.get_token(credential)
print(Api.bills(token))
