from pybitget import Client
from decouple import config
from models.settings import Settings
from pybitget.utils import random_string
from pybitget.enums import *
import threading
import requests
import json

class BG:

    client: Client = None
    init_lock = threading.Lock()

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if BG.client is not None:
                return
        
        # Acquire the lock to ensure only one thread initializes the variables
        with BG.init_lock:
            # Check again after acquiring the lock in case another thread has already initialized the variables
            if BG.client is not None:
                return
            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            passphrase = 'passphrase'
            # Set the variables from shared_vars module
            BG.client = Client(api_key, secret_key, passphrase=passphrase)


    @staticmethod
    def is_contract_exist(coin:str)-> bool:
        try:
            symbols = []
            coin_list = BG.client.mix_get_symbols_info('UMCBL')
            for coin_info in coin_list['data']:
                symbols.append(coin_info['symbol'][:-6])
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist] {e}')

    @staticmethod
    def open_order(ordType: str, coin: str, sd: str, amount_usdt: int, reduceOnly: bool, amount_coins = 0):
        try:
            coin_list = BG.client.mix_get_symbols_info('UMCBL')
            minTradeNum = 0
            sizeMultiplier = 0
            pricePlace = 0
            for coin_info in coin_list['data']:
                if coin_info['symbol'] == f'{coin}_UMCBL':
                    minTradeNum = float(coin_info['minTradeNum'])
                    sizeMultiplier = float(coin_info['sizeMultiplier'])
                    pricePlace = int(coin_info['pricePlace'])
                    break
            curent_price = BG.get_last_price(coin)

            size = amount_usdt / curent_price
            if size % sizeMultiplier != 0:
                size = size - (size % sizeMultiplier)

            if size < minTradeNum:
                size = minTradeNum
            
            side = 'buy_single' if sd == 'Buy' else 'sell_single'

            pr = 0
            if side == 'buy':
                pr = curent_price * (1+0.0001)
            else:
                pr = curent_price * (1-0.0001)
            if reduceOnly == True:
                side = 'sell_single' if sd == 'Buy' else 'buy_single'
                size = amount_coins
            order = BG.client.mix_place_order(symbol=f'{coin}_UMCBL', marginCoin='USDT', size=str(size), side=side, price=round(pr, pricePlace), orderType=ordType, reduceOnly=False)
            print(order)
            return order['data']['orderId'], pr
        except Exception as e:
            print(f'Error: {e}')
            return 0, 0
    
    @staticmethod
    def open_SL(ordType: str, coin: str, sd: str, amount_coins: float, open_price: float, SL_perc: float) -> str:
        try:
            coin_list = BG.client.mix_get_symbols_info('UMCBL')
            minTradeNum = 0
            sizeMultiplier = 0
            pricePlace = 0
            for coin_info in coin_list['data']:
                if coin_info['symbol'] == f'{coin}_UMCBL':
                    minTradeNum = float(coin_info['minTradeNum'])
                    sizeMultiplier = float(coin_info['sizeMultiplier'])
                    pricePlace = int(coin_info['pricePlace'])
                    break
            side = 'sell_single' if sd == 'Buy' else 'buy_single'
            price = 0
            if side == 'sell_single':
                price = open_price * (1-SL_perc)
            elif side == 'buy_single':
                price = open_price * (1+SL_perc)
            size = amount_coins
            executePrice=price * (1 - 0.001) if side == 'sell_single' else price * (1 + 0.001)
            order_type = 'limit' if ordType == 'limit' else 'market'
            order = BG.client.mix_place_plan_order(
                symbol=f'{coin}_UMCBL', 
                marginCoin='USDT', 
                size=str(size), 
                side=side,
                orderType=order_type,
                triggerPrice=round(price, pricePlace), 
                triggerType='fill_price',
                executePrice=round(executePrice, pricePlace),
                reduceOnly=True)
            return order['data']['orderId']
        except Exception as e:
            print(f'Error: {e}')
            return 0, 0

    @staticmethod
    def cancel_tpsl_order(coin, orderId):
        try:
            BG.client.mix_cancel_plan_order(f'{coin}_UMCBL', 'USDT', orderId, planType='normal_plan')
        except Exception as e:
            print(f'Error: {e}')

    
    @staticmethod
    def cancel_normal_order(coin, orderId):
        try:
            BG.client.mix_cancel_order(f'{coin}_UMCBL', 'USDT', orderId)
        except Exception as e:
            print(f'Error: {e}')

    
    @staticmethod
    def cancel_all_orders(coin: str):
        try:
            res = BG.client.mix_get_plan_order_tpsl(f'{coin}_UMCBL', 'UMCBL', True)
            for ord in res['data']:
                res = BG.cancel_tpsl_order(coin, ord['orderId'])
        except Exception as e:
            print(f'Error: {e}')

    @staticmethod
    def get_last_price(coin: str):
        try:
            responce = requests.get(f"https://api.bitget.com/api/v2/mix/market/ticker?productType=USDT-FUTURES&symbol={coin}")
            result = json.loads(responce.text)
            return float(result['data'][0]['lastPr'])
        except Exception as e:
            print(f'Error: {e}')
            return 0
    
    @staticmethod
    def get_balance():
        try:
            result = BG.client.mix_get_accounts(productType='UMCBL')
            return result['data'][0]['usdtEquity']
        except Exception as e:
            print(f'Error: {e}')
            return 0
    
    @staticmethod
    def get_position(coin: str, signal: int) -> dict | None:
        try:
            holdSide = 'long' if signal == 1 else 'short'
            result = BG.client.mix_get_single_position(symbol=f'{coin}_UMCBL', marginCoin='USDT')
            if 'data' in result: 
                if len(result['data']) > 0:
                    for pos in result['data']:
                        if pos['holdSide'] == holdSide:
                            return pos
            return None
        except Exception as e:
            print(f'Error: {e}')
            return 0