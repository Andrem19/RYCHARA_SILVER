import datetime
import hmac
import hashlib
import base64
import requests
import pytz
import json

class Deepcoin:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = 'Pa$$w0rd'

    def _get_timestamp(self):
        return datetime.datetime.now(pytz.utc).isoformat(timespec='milliseconds')

    def _sign(self, timestamp, method, request_path, body=''):
        if isinstance(body, dict):
            body = json.dumps(body)
        prehash = timestamp + method + request_path + body
        signature = hmac.new(self.secret_key.encode(), prehash.encode(), hashlib.sha256)
        return base64.b64encode(signature.digest()).decode()

    def send_request(self, method, request_path, body=''):
        timestamp = self._get_timestamp()
        headers = {
            'DC-ACCESS-KEY': self.api_key,
            'DC-ACCESS-SIGN': self._sign(timestamp, method, request_path, body),
            'DC-ACCESS-TIMESTAMP': timestamp,
            'DC-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        url = 'https://api.deepcoin.com' + request_path
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(body))
        else:
            raise ValueError('Invalid method')
        return response.json()
