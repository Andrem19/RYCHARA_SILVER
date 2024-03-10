import datetime
import hmac
import hashlib
import base64
import requests
import json
import uuid

class Blofin:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = 'oad106'

    def _get_timestamp(self):
        return str(int(datetime.datetime.now().timestamp() * 1000))

    def _get_nonce(self):
        return str(uuid.uuid4())

    def _sign(self, timestamp, nonce, method, request_path, body=''):
        # if isinstance(body, dict):
        if body != '':
            body = json.dumps(body)
        prehash_string = f"{request_path}{method}{timestamp}{nonce}{body}"
        sign = base64.b64encode(hmac.new(self.secret_key.encode(), prehash_string.encode(), hashlib.sha256).hexdigest().encode()).decode()
        return sign
    
    def send_request(self, method, request_path, body=''):
        timestamp = self._get_timestamp()
        nonce = self._get_nonce()
        
        headers = {
            'ACCESS-KEY': self.api_key,
            'ACCESS-SIGN': self._sign(timestamp, nonce, method, request_path, body),
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-NONCE': nonce,
            'ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        url = 'https://openapi.blofin.com' + request_path
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(body))
        else:
            raise ValueError('Invalid method')
        return response.json()
