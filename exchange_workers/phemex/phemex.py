from models.settings import Settings
import helpers.services as serv
from decouple import config
from .client import Client
import requests
import time
import json
import threading
import math
import shared_vars as sv

def round_price(price, tick_size):
    precision = int(round(-math.log(tick_size, 10)))
    return round(price, precision)

def convert_name(name: str):
    res = name.split('-')
    return f'{res[0]}{res[1]}'

class PM:
    client: Client = None
    init_lock = threading.Lock() 
    @staticmethod
    def init(settings: Settings):
        if PM.client is not None:
                return
        
        with PM.init_lock:
            if PM.client is not None:
                return

            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            PM.client = Client(api_key, secret_key)

    @staticmethod
    def get_balance():
        try:
            account = PM.client._send_request('get', '/api-data/futures/v2/tradeAccountDetail')
            if len(account['data'])> 0:
                for acc in account['data']:
                    if acc['currency'] == 'USDT':
                        return float(acc['balanceRv'])
            return 0
        except Exception as e:
            print(f'[get_balance] {e}')

    @staticmethod
    def is_contract_exist(coin: str):
        try:
            list_coins = []
            contracts = PM.client._send_request('get', '/public/products')
            for con in contracts['data']['products']:
                if con['type'] == 'Perpetual':
                    list_coins.append(f"{con['symbol']}T")
            if coin in list_coins:
                return True, list_coins
            return False, list_coins
        except Exception as e:
            print(f'[is_contract_exist] {e}')

    @staticmethod
    def get_last_price(coin: str):
        try:
            c = f'{coin[:-1]}'
            params = {
                'symbol': coin,
            }
            contract = PM.client._send_request('get', '/md/v3/ticker/24hr', params)
            if 'result' in contract:
                return float(contract['result']['lastRp'])
            else: return 0
        except Exception as e:
            print(f'[get_last_price] {e}')