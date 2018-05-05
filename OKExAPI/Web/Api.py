import requests
import os
import json


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


def login(login_credential: LoginCredential) -> str:
    headers = {
        'loginname': login_credential.login_name,
        'content-type': 'application/json',
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

    response = requests.post(
        'https://www.okex.com/v3/users/login/login',
        headers=headers,
        params=params,
        data=str(data)
    ).json()
    return response['data']['token']


def get_cached_token() -> str:
    cached_token_path = '.cached_token'
    if os.path.isfile(cached_token_path):
        return open(cached_token_path, 'r').read()
    return None


def get_token(login_credential: LoginCredential) -> str:
    cached_token = get_cached_token()
    if cached_token:
        return cached_token
    return login(login_credential)


def user_bills(token: str,
               currency_id: int = -1,
               begin_date: int = 0,
               end_date: int = 0,
               is_history: bool = False,
               page: int = 1,
               per_page: int = 20,
               record_type: int = 0):

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
    return response.json()


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
