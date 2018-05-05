import requests
from . import Credential


def login(login_credential: Credential.Credential) -> str:
    headers = {
        'Host': 'www.okex.com',
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
