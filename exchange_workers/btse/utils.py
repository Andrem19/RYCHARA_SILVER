import requests
import time
import hmac
import hashlib

class Client:
    def __init__(self, api_key, secret_key, api_version):
        self.api_key = api_key
        self.secret_key = secret_key
        self.api_version = api_version
        self.host = 'https://api.btse.com/futures'

    def gen_headers(self, path, data=""):
        language = "latin-1"
        nonce = str(int(time.time() * 1000))
        message = path + nonce + data

        signature = hmac.new(
            bytes(self.secret_key, language),
            msg=bytes(message, language),
            digestmod=hashlib.sha384,
        ).hexdigest()

        return {
            "request-api": self.api_key,
            "request-nonce": nonce,
            "request-sign": signature,
            "Accept": "application/json;charset=UTF-8",
            "Content-Type": "application/json",
        }

    def send_request(self, method, endpoint, data=''):
        path = f"/api/{self.api_version}{endpoint}"
        url = self.host + path
        headers = self.gen_headers(path, data)

        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError('Method must be either "GET" or "POST"')

        response.raise_for_status()
        return response.json()
