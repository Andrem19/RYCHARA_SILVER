from models.settings import Settings
import helpers.services as serv
from decouple import config
from exchange_workers.bit_venus_core import Bitvenus
import requests
import json
import threading
import math
import shared_vars as sv

class BV:
    client: Bitvenus = None
    init_lock = threading.Lock() 
    @staticmethod
    def init(settings: Settings):
        if BV.client is not None:
                return
        
        with BV.init_lock:
            if BV.client is not None:
                return

            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            BV.client = Bitvenus(api_key, secret_key)

    @staticmethod
    def get_balance():
        account = BV.client.send_request('GET', '/contract/v1/account')
        if 'USDT' in account:
            return float(account['USDT']['total'])


    @staticmethod
    def is_contract_exist(cn: str):
        contracts = BV.client.send_request('GET', '/v1/contracts')
        list_coins = []
        for cont in contracts:
            parts = cont['symbol'].split('-')
            if len(parts)>=3:
                coin = f'{parts[0]}{parts[2]}'
                list_coins.append(coin)
            
        if cn in list_coins:
            return True, list_coins
        return False, list_coins