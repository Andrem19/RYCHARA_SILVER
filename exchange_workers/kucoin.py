from kucoin_futures.client import Trade
from kucoin_futures.client import Market
from kucoin_futures.client import User
from models.settings import Settings
from decouple import config
import requests
import json
import threading
import math

def round_price(price, tick_size):
    precision = int(round(-math.log(tick_size, 10)))
    return round(price, precision)

class KuCoin:

    @staticmethod
    def open_limit_order(coin: str, sd: str, amount_usdt: int):
        try:
            curent_price = KuCoin.get_last_price(coin)
            contract_info = KuCoin.market_client.get_contract_detail(f'{coin}M')
            max_leverage = int(contract_info['maxLeverage'])
            lot = (amount_usdt / curent_price) // contract_info['multiplier']
            lev = 20 if max_leverage >= 20 else max_leverage
            side = 'buy' if sd == 'Buy' else 'sell'

            pr = 0
            if side == 'buy':
                pr = curent_price * (1+0.0001)
            else:
                pr = curent_price * (1-0.0001)
            if lot < 1:
                lot = 1
            price = round_price(pr, contract_info['tickSize'])
            order_id = KuCoin.client.create_limit_order(symbol=f'{coin}M', side=side, lever=f'{lev}', size=int(lot), price=price)
            return order_id['orderId'], pr
        except Exception as e:
            print(f'Error [open_limit_order]: {e}')
            return 0, 0
    
    @staticmethod
    def open_market_order(coin: str, sd: str, amount_usdt: int) -> str:
        try:
            curent_price = KuCoin.get_last_price(coin)
            contract_info = KuCoin.market_client.get_contract_detail(f'{coin}M')
            max_leverage = int(contract_info['maxLeverage'])
            lot = (amount_usdt / curent_price) // contract_info['multiplier']
            side = 'buy' if sd == 'Buy' else 'sell'
            lev = 20 if max_leverage >= 20 else max_leverage
            order_id = KuCoin.client.create_market_order(symbol=f'{coin}M', side=side, lever=f'{lev}', size=int(lot), closeOrder=False)
            return order_id, curent_price
        except Exception as e:
            print(f'Error [open_market_order]: {e}')
            return 0, 0
    
    @staticmethod
    def cancel_order_byId(order_id: str) -> str:
        try:
            result = KuCoin.client.cancel_order(orderId=order_id)
            print(result)
        except Exception as e:
            print(f'Error: {e}')
    @staticmethod
    def cancel_all_orders(coin: str) -> str:
        try:
            result = KuCoin.client.cancel_all_stop_order(symbol=f'{coin}M')
            print(result)
        except Exception as e:
            print(f'Error [cancel_all_orders]: {e}')

    @staticmethod
    def close_position_market(coin: str, sd: str) -> str:
        try:
            side = 'buy' if sd == 'Sell' else 'sell'
            order_id = KuCoin.client.create_market_order(symbol=f'{coin}M', side=side, lever='10', closeOrder=True)
            return order_id
        except Exception as e:
            print(f'Error [close_position_market]: {e}')
            return 0
    
    @staticmethod
    def get_position(coin: str):
        try:
            position = KuCoin.client.get_position_details(f'{coin}M') # 'unrealisedPnl' 'currentQty'/0
            return position
        except Exception as e:
            print(f'Error [get_position]: {e}')
            return 0
    
    @staticmethod
    def open_SL(coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float) -> str:
        try:
            side = 'buy' if sd == 'Sell' else 'sell'
            st = 'down' if side =='sell' else 'up'
            contract_info = KuCoin.market_client.get_contract_detail(f'{coin}M')
            price = 0
            if side == 'buy':
                price = open_price * (1+SL_perc)
            elif side == 'sell':
                price = open_price * (1-SL_perc)
            price = round_price(price, contract_info['tickSize'])
            order_id = KuCoin.client.create_limit_order(symbol=f'{coin}M', side=side, size=amount_lot, lever='10', closeOrder=True, stopPriceType='IP', price=price, stopPrice=price, stop=st)
            return order_id['orderId']
        except Exception as e:
            print(f'Error [open_SL]: {e}')
            return 0
    
    @staticmethod
    def trailing_SL(coin: str, sd: str, amount_lot: str, price: float) -> str:
        try:
            side = 'buy' if sd == 'Sell' else 'sell'
            st = 'down' if side =='sell' else 'up'
            contract_info = KuCoin.market_client.get_contract_detail(f'{coin}M')
            price = round_price(price, contract_info['tickSize'])
            order_id = KuCoin.client.create_limit_order(symbol=f'{coin}M', side=side, size=amount_lot, lever='10', closeOrder=True, stopPriceType='IP', price=price, stopPrice=price, stop=st)
            return order_id['orderId']
        except Exception as e:
            print(f'Error [trailing_SL]: {e}')
            return 0
    

    @staticmethod
    def open_TP(coin: str, sd: str, amount_lot: str, open_price: float, TP_perc: float) -> str:
        try:
            side = 'buy' if sd == 'Sell' else 'sell'
            st = 'up' if side =='sell' else 'down'
            price = 0
            if side == 'buy':
                price = open_price * (1-TP_perc)
            elif side == 'sell':
                price = open_price * (1+TP_perc)
            contract_info = KuCoin.market_client.get_contract_detail(f'{coin}M')
            price = round_price(price, contract_info['tickSize'])
            order_id = KuCoin.client.create_limit_order(symbol=f'{coin}M', side=side, size=amount_lot, lever='10', closeOrder=True, stopPriceType='TP', price=price, stopPrice=price, stop=st)
            return order_id
        except Exception as e:
            print(f'Error [open_TP]: {e}')
            return 0
    
    @staticmethod
    def get_last_price(coin):
        try:
            tk = KuCoin.market_client.get_ticker(f'{coin}M')
            curent_price = float(tk['price'])
            return curent_price
        except Exception as e:
            print(f'Error [get_last_price]: {e}')
            return 0
    @staticmethod
    def is_contract_exist(coin:str)-> (bool, list):
        try:
            response = requests.get('https://api-futures.kucoin.com/api/v1/contracts/active')
            data = json.loads(response.text)
            symbols = []
            if len(data) > 0:
                for contract in data['data']:
                    s = contract['symbol'][:-1]
                    symbols.append(s)
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist] {e}')
         
    @staticmethod
    def get_balance(coin: str):
        try:
            result = KuCoin.user_client.get_account_overview(currency=coin) # 'availableBalance' 'accountEquity'
            return result['accountEquity']
        except Exception as e:
            print(f'Error [get_balance]: {e}')
            return 0
    
    


    client: Trade = None
    market_client: Market = None
    user_client: User = None
    init_lock = threading.Lock() 

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if KuCoin.client is not None:
                return
        
        # Acquire the lock to ensure only one thread initializes the variables
        with KuCoin.init_lock:
            # Check again after acquiring the lock in case another thread has already initialized the variables
            if KuCoin.client is not None:
                return
            
            # Set the variables from shared_vars module
            KuCoin.user_client = User(key=config(settings.API_KEY), secret=config(settings.SECRET_KEY), passphrase='passphrase', is_sandbox=False, url='https://api-futures.kucoin.com')
            KuCoin.market_client = Market(url='https://api-futures.kucoin.com')
            KuCoin.client = Trade(key=config(settings.API_KEY), secret=config(settings.SECRET_KEY), passphrase='passphrase', is_sandbox=False, url='https://api-futures.kucoin.com')