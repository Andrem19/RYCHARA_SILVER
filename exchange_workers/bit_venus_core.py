import urllib.parse
import hmac
import hashlib
import base64
import requests
import datetime
import pytz
import json

class Bitvenus:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def _get_timestamp(self):
        return str(int(datetime.datetime.now(pytz.utc).timestamp() * 1000))

    def _sign(self, params):
        query_string = '&'.join(["{}={}".format(d, params[d]) for d in params])
        signature = hmac.new(bytes(self.secret_key, 'latin-1'), msg = bytes(query_string, 'latin-1'), digestmod = hashlib.sha256).hexdigest()
        return signature

    def send_request(self, method, request_path, params={}, body=''):
        params['timestamp'] = self._get_timestamp()
        params['signature'] = self._sign(params)
        headers = {
            'X-BH-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        url = 'https://www.bitvenus.me/openapi' + request_path
        # print(url)
        # print(params)
        # print(headers)
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(body))
        else:
            raise ValueError('Invalid method')
        # print(response.text)
        return response.json()

