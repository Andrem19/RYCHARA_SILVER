from models.settings import Settings
import helpers.services as serv
from decouple import config
from exchange_workers.blofin.blofin_core import Blofin
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

class BF:
    client: Blofin = None
    init_lock = threading.Lock() 
    @staticmethod
    def init(settings: Settings):
        if BF.client is not None:
                return
        
        with BF.init_lock:
            if BF.client is not None:
                return

            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            BF.client = Blofin(api_key, secret_key)

    @staticmethod
    def get_balance():
        try:
            account = BF.client.send_request('GET', '/api/v1/asset/balances?accountType=futures')
            if 'data' in account:
                return float(account['data'][0]['balance'])
        except Exception as e:
            print(f'[get_balance] {e}')
    
    @staticmethod
    def get_last_price(coin: str):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            contract = BF.client.send_request('GET', f'/api/v1/market/mark-price?instId={c}')
            if 'data' in contract:
                return float(contract['data'][0]['markPrice'])
            else: return 0
        except Exception as e:
            print(f'[get_last_price] {e}')

    @staticmethod
    def is_contract_exist(cn: str):
        try:
            contracts = BF.client.send_request('GET', '/api/v1/market/instruments')
            list_coins = []
            if 'data' in contracts:
                for cont in contracts['data']:
                    parts = cont['instId'].split('-')
                    if len(parts)>=2:
                        coin = f'{parts[0]}{parts[1]}'
                        list_coins.append(coin)
                    
                if cn in list_coins:
                    return True, list_coins
                return False, list_coins
        except Exception as e:
            print(f'[is_contract_exist] {e}')

    @staticmethod
    def instrument_info(coin: str) -> dict:
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            instrument = BF.client.send_request('GET', f'/api/v1/market/instruments?instId={c}')
            if 'data' in instrument:
                if len(instrument['data'])> 0:
                    return instrument['data'][0] #'contractValue': '100' 'maxLeverage': '50' 'minSize': '1', 'lotSize': '1', 'tickSize': '0.0001'
            return {}
        except Exception as e:
            print(f'[instrument_info] {e}')

    @staticmethod
    def get_position(coin: str) -> dict | None:
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            result = BF.client.send_request('GET', f'/api/v1/account/positions?instId={c}')
            if 'data' in result:
                if len(result['data']) > 0:
                    return result['data'][0] #'averagePrice': '10.743000000000000000' 'unrealizedPnl': '-0.0 'leverage': '3' 'positions': '-1'
            return None
        except Exception as e:
            print(f'[get_position]: {e}')
            return 0
        
    @staticmethod
    def set_leverage(coin: str, leverage: int, max_leverage: int):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            leverage = max_leverage if leverage > max_leverage else leverage
            body = {
                "instId": c,
                "leverage":str(leverage),
                "marginMode":"cross"
            }
            result = BF.client.send_request('POST', f'/api/v1/account/set-leverage', body)
            print(result)
        except Exception as e:
            print(f'[set_leverage]: {e}')
            return 0
        
    @staticmethod
    def is_any_position_exists():
        try:
            position_list = []
            result = BF.client.send_request('GET', f'/api/v1/account/positions')
            print(result)
            if 'data' in result:
                if len(result['data'])>0:
                    for res in result['data']:
                        sd = 'Buy' if float(res['positions']) > 0 else 'Sell'
                        amt = float(res['positions'])
                        name = convert_name(res['instId'])
                        inst = [name, sd, amt]
                        position_list.append(inst)
            return position_list
        except Exception as e:
            print(f'Error [is_any_position_exists]: {e}')
            return [1]
    
    @staticmethod
    def cancel_all_orders(coin: str, tp_sl: bool):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            if tp_sl:
                all_orders = BF.client.send_request('GET', f'/api/v1/trade/orders-tpsl-pending?instId={c}')
            else:   
                all_orders = BF.client.send_request('GET', f'/api/v1/trade/orders-pending?instId={c}')
            if 'data' in all_orders:
                if len(all_orders['data'])>0:
                    for order in all_orders['data']:
                        
                        if tp_sl:
                            body = [{
                            "instId": c,
                            "tpslId": order["tpslId"],
                            "clientOrderId": ""
                            }]
                            ord = BF.client.send_request('POST', '/api/v1/trade/cancel-tpsl', body)
                        else:
                            body = {
                            "orderId": order["orderId"]
                            }
                            ord = BF.client.send_request('POST', '/api/v1/trade/cancel-order', body)
        except Exception as e:
            print(f'Error [cancel_all_orders]: {e}')
            return 0
        
    @staticmethod
    def open_market_order(coin: str, sd: str, amount_usdt: int, reduceOnly: bool, amount_coins = 0):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            last_price = BF.get_last_price(coin)
            instr_info = BF.instrument_info(coin)
            size = (amount_usdt / last_price) // float(instr_info['contractValue'])
            tickSz = float(instr_info['tickSize'])
            max_lev = int(instr_info['maxLeverage'])
            if size < 1:
                size = 1
            if not reduceOnly:
                time.sleep(1.1)
                BF.set_leverage(coin, 20, max_lev)

            body = {
                "instId": c,
                "marginMode":"cross",
                "side": sd.lower(),
                "orderType": 'market',
                "size": str(int(size)),
            }
            if reduceOnly == True:
                body['side'] = 'buy' if sd == 'Sell' else 'sell'
                body['reduceOnly'] = 'true'
                body['size'] = str(amount_coins)

            ord = BF.client.send_request('POST', '/api/v1/trade/order', body)
            print(ord)
            if 'data' in ord:
                if len(ord['data'])>0:
                    return ord['data'][0]['orderId'], last_price
            return 0, last_price
        except Exception as e:
            print(f'Error [open_market_order]: {e}')
            return 0, 0

    @staticmethod
    def open_SL(coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            instr_info = BF.instrument_info(coin)
            tickSz = float(instr_info['tickSize'])
            side = 'sell' if sd == 'Buy' else 'buy'

            price = 0
            if sd == 'Buy':
                price = open_price * (1-SL_perc)
            elif sd == 'Sell':
                price = open_price * (1+SL_perc)
            price = round_price(price, tickSz)
            executive_price = price * (1 + 0.001) if side == 'Sell' else price * (1 - 0.001)
            executive_price = round_price(executive_price, tickSz)

            body = {
                "instId": c,
                "marginMode": "cross",
                "positionSide": 'net',
                "side": side,
                "slTriggerPrice": str(price),
                "slOrderPrice": str(executive_price),
                "size": str(int(amount_lot)),
                "reduceOnly": "true",
                }
            print(body)
            ord = BF.client.send_request('POST', '/api/v1/trade/order-tpsl', body)
            print(ord)
            if 'data' in ord:
                if len(ord['data'])>0:
                    return ord['data']['tpslId']
            return 0
        except Exception as e:
            print(f'Error [open_SL]: {e}')
            return 0