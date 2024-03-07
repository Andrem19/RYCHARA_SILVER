from models.settings import Settings
import helpers.services as serv
from decouple import config
from exchange_workers.deepcoin_core import Deepcoin
import requests
import json
import threading
import math

class DC:
    client: Deepcoin = None
    init_lock = threading.Lock() 
    @staticmethod
    def init(settings: Settings):
        if DC.client is not None:
                return
        
        with DC.init_lock:
            if DC.client is not None:
                return

            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            DC.client = Deepcoin(api_key, secret_key)

    @staticmethod
    def get_balance():
        account = DC.client.send_request('GET', '/deepcoin/account/balances?instType=SWAP&ccy=USDT')
        if 'data' in account:
            return float(account['data'][0]['bal'])
