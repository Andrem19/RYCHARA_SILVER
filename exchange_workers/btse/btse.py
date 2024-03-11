from models.settings import Settings
from decouple import config
import threading
from datetime import datetime
import helpers.services as serv
from exchange_workers.btse.utils import Client
import traceback

class BTSE:

    client: Client = None
    # standart: Standard = None
    init_lock = threading.Lock()

    @staticmethod
    def init(settings: Settings):
        if BTSE.client is not None:
                return
        
        with BTSE.init_lock:
            if BTSE.client is not None:
                return
            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            BTSE.client = Client(api_key, secret_key, 'v2.1')

    @staticmethod
    def is_contract_exist(coin: str):
        try:
            list_coins = []
            contracts = BTSE.client.send_request('GET', '/market_summary')
            for con in contracts:
                cn = f'{con["symbol"][:-3]}USDT'
                list_coins.append(cn)
            if coin in list_coins:
                return True, list_coins
            return False, list_coins
        except Exception as e:
            print(f'[is_contract_exist] {e}')