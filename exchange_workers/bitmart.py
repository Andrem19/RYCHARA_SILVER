from bitmart.api_contract import APIContract
from bitmart.api_account import APIAccount
from models.settings import Settings
from bitmart.lib import cloud_utils, cloud_exceptions
from bitmart.lib.cloud_log import CloudLog
import requests
from decouple import config
import threading
import math
import json

def round_price(price, tick_size):
    precision = int(round(-math.log(tick_size, 10)))
    return round(price, precision)

class BM:
    CloudLog.logger_level = 'info'
    client: APIContract = None
    account: APIAccount = None
    # standart: Standard = None
    init_lock = threading.Lock()

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if BM.client is not None:
                return
        
        # Acquire the lock to ensure only one thread initializes the variables
        with BM.init_lock:
            # Check again after acquiring the lock in case another thread has already initialized the variables
            if BM.client is not None:
                return
            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            # Set the variables from shared_vars module
            BM.client = APIContract(api_key, secret_key, 'trade', timeout=(3, 10))
            BM.account = APIAccount(api_key, secret_key, 'trade', timeout=(3, 10))
            # BX.standard = Standard(api_key, secret_key)

    @staticmethod
    def re_init(settings: Settings):
        BM.client = None
        BM.init(settings)

    @staticmethod
    def get_last_price(coin):
        try:
            # marketDataAPI =  MarketData.MarketAPI(flag='0')
            c = f'{coin[:-4]}-{coin[-4:]}'
            response = requests.get(f'https://api-cloud.bitmart.com/contract/public/details?symbol={coin}')
            res = response.json()
            if 'data' in res:
                return float(res['data']['symbols'][0]['last_price'])
        except Exception as e:
            print(f'Error [get_last_price]: {e}')
            return 0
    @staticmethod
    def is_contract_exist(coin:str)-> (bool, list):
        try:
            symbols = []
            res = requests.get('https://api-cloud.bitmart.com/contract/public/details')
            data = json.loads(res.text)
            for contract in data['data']['symbols']:
                symbols.append(contract['symbol'])
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist] {e}')

    @staticmethod
    def get_balance():
        try:
            account = BM.client.get_assets_detail()
            if 'data' in account[0]:
                if len(account[0]['data']) > 0:
                    return account[0]['data'][0]['equity']
        except Exception as e:
            print(f'Error: {e}')
            return 0
    
    @staticmethod
    def get_position(coin: str):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            pos = BM.client.get_position(contract_symbol=coin)
            position = pos[0]
            if 'data' in position:
                if len(position['data']) > 0:
                    return position['data'][0] # [] data empty if no position // open_avg_price current_amount unrealized_value
                else: return None
            return None
        except Exception as e:
            print(f'Error [get_position]: {e}')
            return 0
        
    @staticmethod
    def cancel_all_orders(coin: str) -> str:
        try:
            BM.client.post_cancel_orders(contract_symbol=coin)
        except Exception as e:
            print(f'Error [cancel_all_orders]: {e}')
    
    @staticmethod
    def cancel_trigger_order(coin: str, ord_id) -> str:
        try:
            BM.client.post_cancel_plan_order(contract_symbol=coin, order_id=str(ord_id))
        except Exception as e:
            print(f'Error [cancel_all_orders]: {e}')
    
    @staticmethod
    def open_order(ordType: str, coin: str, sd: str, amount_usdt: int, reduceOnly: bool, amount_coin: float = 0):
        try:
            response = requests.get(f'https://api-cloud.bitmart.com/contract/public/details?symbol={coin}')
            res = response.json()

            last_price = float(res['data']['symbols'][0]['last_price'])
            price_precision = float(res['data']['symbols'][0]['price_precision'])
            contract_size = float(res['data']['symbols'][0]['contract_size'])
            max_lever = int(res['data']['symbols'][0]['max_leverage'])
            if reduceOnly:
                side = 3 if sd == 'Buy' else 2
            else:
                side = 1 if sd == 'Buy' else 4

            size = (amount_usdt / last_price) // contract_size
            # if size % vol_precision != 0:
            #     size = size - (size % vol_precision)

            pr = 0
            if sd == 'Buy':
                pr = last_price * (1+0.001)
            else:
                pr = last_price * (1-0.001)
            if reduceOnly:
                size = amount_coin
            price = round_price(pr, price_precision)
            lev = 20 if max_lever >= 20 else max_lever
            BM.client.post_submit_leverage(coin, 'cross', f'{lev}')
            order = BM.client.post_submit_order(contract_symbol=coin, type=ordType, side=side, leverage=f'{lev}', open_type='cross', price=str(price), size=int(size), mode=1)
            return order[0]['data']['order_id'], pr
        except Exception as e:
            print(f'Error [open_order]: {e}')
            return 0
        
    @staticmethod
    def open_SL(ordType: str, coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
        try:
            response = requests.get(f'https://api-cloud.bitmart.com/contract/public/details?symbol={coin}')
            res = response.json()

            last_price = float(res['data']['symbols'][0]['last_price'])
            price_precision = float(res['data']['symbols'][0]['price_precision'])
            contract_size = float(res['data']['symbols'][0]['contract_size'])

            side = 3 if sd == 'Buy' else 2
            price_way = 1 if sd == 'Sell' else 2
            price = 0
            if sd == 'Buy':
                price = open_price * (1-SL_perc)
            elif sd == 'Sell':
                price = open_price * (1+SL_perc)
            price = round_price(price, price_precision)
            executive_price = price * (1 + 0.001) if side == 'Sell' else price * (1 - 0.001)
            executive_price = round_price(executive_price, price_precision)
            order = BM.client.post_submit_plan_order(
                contract_symbol=coin,
                type=ordType,
                side=side,
                leverage='10',
                open_type='cross',
                size=int(amount_lot),
                trigger_price=str(price),
                executive_price=str(executive_price),
                price_way=price_way,
                price_type=2,
                mode=1
            )
            return order[0]['data']['order_id']
        except Exception as e:
            print(f'Error [open_SL]: {e}')
            return 0