import json


class Credential:

    def __init__(self, area_code: str, login_name: str, password: str):
        self.area_code = area_code
        self.login_name = login_name
        self.password = password

    @staticmethod
    def load_from_file(file_path):
        json_data = json.loads(open(file_path, 'r').read())
        return Credential(
            json_data['areaCode'],
            json_data['loginName'],
            json_data['password']
        )