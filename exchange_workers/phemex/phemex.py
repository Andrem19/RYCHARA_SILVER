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

    @staticmethod
    def instrument_info(coin: str) -> dict:
        try:
            c = f'{coin[:-1]}'
            contracts = PM.client._send_request('get', '/public/products')
            for con in contracts['data']['products']:
                if con['type'] == 'Perpetual' and con['symbol']==c:#'contractSize': 5.0, 'lotSize': 1, 'tickSize': 0.0001, 'priceScale': 4, 'pricePrecision': 4, 'maxLeverage': 100
                    return con
        except Exception as e:
            print(f'[instrument_info] {e}')

    @staticmethod
    def set_leverage(coin: str, leverage: int, max_leverage: int):
        try:
            lev = max_leverage if leverage>max_leverage else leverage
            params = {
                'symbol': coin,
                'leverageRr': str(lev),
            }
            PM.client._send_request('PUT', '/g-positions/leverage', params)
        except Exception as e:
            print(f'[set_leverage]: {e}')
            return 0

    @staticmethod
    def is_any_position_exists():
        try:
            position_list = []
            result = PM.client.query_account_n_positions('USDT')
            print(result)
            if 'data' in result:
                if 'positions' in result['data']:
                    for pos in result['data']['positions']:
                        if float(pos['size']) != 0:
                            sd = pos['side']
                            amt = float(pos['size'])
                            name = pos['symbol']
                            inst = [name, sd, amt]
                            position_list.append(inst)
            return position_list
        except Exception as e:
            print(f'Error [is_any_position_exists]: {e}')
            return [1]

    @staticmethod
    def cancel_all_orders(coin: str):
        try:
            PM.client.cancel_all(coin)
        except Exception as e:
            print(f'Error [cancel_all_orders]: {e}')

    @staticmethod
    def switch_pos_mode(coin: str):
        try:
            params = {
                'symbol': coin,
                'targetPosMode': 'OneWay',
            }
            PM.client._send_request('PUT', '/g-positions/switch-pos-mode-sync', params)
        except Exception as e:
            print(f'Error [switch_pos_mode]: {e}')


    @staticmethod
    def get_position(coin: str) -> dict | None:
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            params = {
                'currency': 'USDT',
                'symbol': coin
            }
            result = PM.client._send_request('GET', '/g-accounts/accountPositions', params)
            if 'data' in result:
                if len(result['data']['positions']) > 0:
                    return result['data']['positions'][0] #'size': '31' 'avgEntryPriceRp': '0.6257'
            return None
        except Exception as e:
            print(f'[get_position]: {e}')
            return 0

    @staticmethod
    def open_market_order(coin: str, sd: str, amount_usdt: int, reduceOnly: bool, sl_perc: float, amount_coins = 0):
        try:
            last_price = PM.get_last_price(coin)
            instr_info = PM.instrument_info(coin)
            lot_size = int(instr_info['lotSize'])
            price_prec = int(instr_info['pricePrecision'])
            size = (amount_usdt / last_price)
            size = math.floor(size / lot_size) * lot_size
            
            max_lev = int(instr_info['maxLeverage'])
            
            if not reduceOnly:
                PM.switch_pos_mode(coin)
                PM.set_leverage(coin, 20, max_lev)

            price = 0
            if sd == 'Buy':
                price = last_price * (1-sl_perc)
            elif sd == 'Sell':
                price = last_price * (1+sl_perc)
            price = round(price, price_prec)
            triger_price = price * (1 - 0.001) if sd == 'Sell' else price * (1 + 0.001)
            triger_price = round(triger_price, price_prec)
            params = {
                "symbol": coin,
                "reduceOnly":"false",
                "orderQtyRq": str(size),
                "ordType": 'Market',
                "side": sd,
                "posSide": 'Merged',
                "stopLossRp": str(triger_price),
                "slPxRp": str(price),
            }
            
            if reduceOnly == True:
                params['side'] = 'Buy' if sd == 'Sell' else 'Sell'
                params['reduceOnly'] = 'true'
                params['orderQtyRq'] = str(amount_coins)
                del params['stopLossRp']
                del params['slPxRp']
                
            ord = PM.client._send_request('PUT', '/g-orders/create', params)
            if 'data' in ord:
                return ord['data']['orderID'], last_price
            return 0, last_price
        except Exception as e:
            print(f'Error [open_market_order]: {e}')
            return 0, 0

    @staticmethod
    def open_SL(coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
        try:
            instr_info = PM.instrument_info(coin)
            price_prec = int(instr_info['pricePrecision'])
            side = 'Buy' if sd == 'Sell' else 'Sell'

            price = 0
            if sd == 'Buy':
                price = open_price * (1-SL_perc)
            elif sd == 'Sell':
                price = open_price * (1+SL_perc)
            price = round(price, price_prec)
            triger_price = price * (1 + 0.001) if sd == 'Sell' else price * (1 - 0.001)
            triger_price = round(triger_price, price_prec)

            params = {
                "symbol": coin,
                "side": side,
                "posSide": 'Merged',
                "reduceOnly":"true",
                "ordType": 'StopLimit',
                "stopLossRp": str(triger_price),
                "slPxRp": str(price),
                "orderQtyRq": str(amount_lot),                
            }
            print(params)
            ord = PM.client._send_request('PUT', '/g-orders/create', params)
            print(ord)
            # if 'data' in ord:
            #     return ord['data']['orderID']
            # return 0
        except Exception as e:
            print(f'Error [open_SL]: {e}')
            return 0