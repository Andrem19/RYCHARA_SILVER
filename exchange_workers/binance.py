import requests
import numpy as np
#pip install binance-futures-connector
from binance.um_futures import UMFutures
from binance.error import Error, ClientError
from models.settings import Settings
from decouple import config
from datetime import datetime
import threading
import helpers.services as serv
from retry import retry

MAXIMUM_NUMBER_OF_API_CALL_TRIES = 3

def get_kline(coin: str, number_candles: int, interv: int):
        try:
            endpoint = f'/fapi/v1/klines?symbol={coin}&interval={interv}m&limit={number_candles}'
            url = 'https://fapi.binance.com' + endpoint
            response = requests.get(url).json()

            new_list = [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in response]
            return np.array(new_list)
        except Exception as e:
            print(f'Error: {e}')
            return 0
def create_client():
    api_key = config('BNAPI_1')
    secret_key = config('BNSECRET_1')
    BN.client = UMFutures(key=api_key, secret=secret_key)

class BN:

    client: UMFutures = None
    init_lock = threading.Lock()

    @staticmethod
    def init(settings: Settings):
        if BN.client is not None:
                return
        
        with BN.init_lock:
            if BN.client is not None:
                return
            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            params = {
                'timeout': 14,
            }
            BN.client = UMFutures(key=api_key, secret=secret_key, **params)

    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def get_last_price(coin: str):
        try:
            create_client()#TODO try it
            tick = BN.client.ticker_price(symbol=coin)
            return float(tick['price'])
        except Error as e:
            print(f'Error [get_last_price]: {e}')
            return 0
    
    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def get_balance():
        try:
            create_client() # TODO try it
            result = BN.client.balance()
            usdt = None
            for asset in result:
                if asset['asset'] == 'USDT':
                    usdt = asset
            
            if usdt is None:
                return 0
            return usdt['balance']
        except Error as e:
            print(f'Error: {e}')
            return 0
    
    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def cancel_all_orders(coin: str):
        try:
            create_client() #TODO try it
            BN.client.cancel_open_orders(symbol=coin)
        except Error as e:
            print(f'Error: {e}')

    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def get_position(coin: str) -> dict:
        try:
            create_client() #TODO try it
            result = BN.client.account()['positions'] # unrealizedProfit entryPrice positionAmt
            for res in result:
                if res['symbol'] == coin:
                    return res
        except Error as e:
            print(f'Error: {e}')
            return 0
        
    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def is_any_position_exists():
        try:
            position_list = []
            create_client() #TODO try it
            result = BN.client.account()['positions'] # unrealizedProfit entryPrice positionAmt
            for res in result:
                if float(res['positionAmt']) != 0:
                    sd = 'Buy' if float(res['positionAmt']) > 0 else 'Sell'
                    amt = serv.get_position_lots(res, 'BN')
                    name = res['symbol']
                    inst = [name, sd, amt]
                    position_list.append(inst)
            return position_list
        except Error as e:
            print(f'Error: {e}')
            return 0

    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def is_contract_exist(coin:str)-> (bool, list):
        try:
            create_client()#TODO try it
            symbols = []
            coin_list = BN.client.exchange_info()
            for symbol in coin_list['symbols']:
                if symbol['contractType'] == 'PERPETUAL':
                    symbols.append(symbol['symbol'])
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist] {datetime.now()} {e}')
        
    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def get_symbol_info(coin: str) -> dict:
        try:
            create_client() #TODO try it
            sym = None
            coin_list = BN.client.exchange_info()
            for symbol in coin_list['symbols']:
                if symbol['symbol'] == coin:
                    sym = symbol
            return sym
        except Exception as e:
            print(f'Error[get_symbol_info {datetime.now()}]: {e}')
            return 0
    
    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def open_order(ordType: str, coin: str, sd: str, amount_usdt: int, reduceOnly: bool, amount_coins: int = 0):
        try:
            create_client() #TODO try it
            BN.client.change_leverage(coin, 20)
            coin_info = BN.get_symbol_info(coin)
            quantityPrecision = coin_info['quantityPrecision']
            pricePrecision = coin_info['pricePrecision']
            minQy = 0
            filters = coin_info['filters']
            for filter in filters:
                if filter['filterType'] == 'LOT_SIZE':
                    minQty = float(filter['minQty'])
            curent_price = BN.get_last_price(coin)

            size = amount_usdt / curent_price

            if size % minQty != 0:
                size = size - (size % minQty)

            side = 'BUY' if sd == 'Buy' else 'SELL'
            pr = 0
            if side == 'BUY':
                pr = round(curent_price * (1+0.0001), pricePrecision)
            else:
                pr = round(curent_price * (1-0.0001), pricePrecision)
            params = {
                'quantity': round(size, quantityPrecision),
            }
            if ordType == 'limit':
                params['timeInForce'] = 'GTC'
                params['price'] = pr
                
            if reduceOnly:
                side = 'SELL' if sd == 'Buy' else 'BUY'
                params['quantity'] =  abs(amount_coins)
                # params['closePosition'] = 'true'
                # params.pop('quantity')
            order = BN.client.new_order(symbol=coin, side=side, type=ordType.upper(), **params)

            return order['clientOrderId'], pr
        except Error as e:
            print(f'Error [open_order {datetime.now()}]: {e}')
            return 0, 0
        
    @staticmethod
    @retry(Exception, tries=MAXIMUM_NUMBER_OF_API_CALL_TRIES, delay=2)
    def open_SL(ordType: str, coin: str, sd: str, amount_coins: float, open_price: float, SL_perc: float) -> str:
        try:
            create_client() #TODO try it
            coin_info = BN.get_symbol_info(coin)
            quantityPrecision = coin_info['quantityPrecision']
            pricePrecision = coin_info['pricePrecision']

            side = 'SELL' if sd == 'Buy' else 'BUY'

            price = 0
            if side == 'SELL':
                price = open_price * (1-SL_perc)
            elif side == 'BUY':
                price = open_price * (1+SL_perc)

            oType = 'STOP_MARKET' if ordType == 'market' else 'STOP'

            executePrice=price * (1 - 0.001) if side == 'SELL' else price * (1 + 0.001)
            params = None
            if ordType == 'limit':
                params = {
                    'price': round(price, pricePrecision),
                    'stopPrice': round(executePrice, pricePrecision),
                    'timeInForce': 'GTC',
                    'quantity': abs(amount_coins)
                }
            elif ordType == 'market':
                params = {
                    'closePosition': 'true',
                    'stopPrice': round(price, pricePrecision)
                }

            order = BN.client.new_order(symbol=coin, side=side, type=oType, **params)
            return order['clientOrderId']
        except Error as e:
            print(f'Error [openSL {datetime.now()}]: {e}')
            return 0, 0