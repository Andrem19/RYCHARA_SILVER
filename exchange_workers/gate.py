import gate_api
from gate_api.exceptions import ApiException, GateApiException
from decouple import config
import threading
import logging
import time
from decimal import Decimal as D, ROUND_UP, getcontext
from models.settings import Settings
from gate_api import ApiClient, Configuration, FuturesApi, FuturesOrder, WalletApi, FuturesPriceTriggeredOrder, FuturesPriceTrigger, FuturesInitialOrder
from gate_api.exceptions import GateApiException
import math

def round_price(price, tick_size):
    precision = int(round(-math.log(tick_size, 10)))
    return round(price, precision)

class GT:

    config: Configuration = None
    futures_api: FuturesApi = None
    init_lock = threading.Lock()
    logger = logging.getLogger(__name__)

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if GT.futures_api is not None:
                return
        
        with GT.init_lock:

            if GT.futures_api is not None:
                return
            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)

            GT.config = Configuration(key=api_key, secret=secret_key, password='190990')
            GT.futures_api = FuturesApi(ApiClient(GT.config))
    
    @staticmethod
    def get_last_price(coin: str):
        try:
            c = f'{coin[:-4]}_{coin[-4:]}'
            tickers = GT.futures_api.list_futures_tickers('usdt', contract=c)
            assert len(tickers) == 1
            last_price = tickers[0].last
            
            return float(last_price)
        except GateApiException as e:
            print(f'Error [get_last_price]: {e}')
            return 0
    

    @staticmethod
    def is_contract_exist(coin:str)-> (bool, list):
        try:
            data = GT.futures_api.list_futures_contracts(settle='usdt')
            symbols = []
            for contract in data:
                s = f'{contract.name[:-5]}{contract.name[-4:]}'
                symbols.append(s)
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist] {e}')


    @staticmethod
    def get_balance() -> float:
        try:
            futures_account = GT.futures_api.list_futures_accounts('usdt')
            total = futures_account.total
            return total
        except GateApiException as e:
            print(f'Error [get_balance]: {e}')
            return 0

    @staticmethod
    def cancel_all_orders(coin: str) -> str:
        try:
            c = f'{coin[:-4]}_{coin[-4:]}'
            GT.futures_api.cancel_futures_orders('usdt', c)
        except GateApiException as e:
            print(f'Error [cancel_all_orders]: {e}')
    
    @staticmethod
    def cancel_trigger_all_orders(ord_id) -> str:
        try:
            GT.futures_api.cancel_price_triggered_order('usdt', ord_id)
        except GateApiException as e:
            print(f'Error [cancel_all_orders]: {e}')
    
    @staticmethod
    def get_position(coin: str):
        try:
            c = f'{coin[:-4]}_{coin[-4:]}'
            positions = GT.futures_api.get_position('usdt', c) #entry_price=0 unrealised_pnl size
            pos = {
                'entry_price': float(positions.entry_price),
                'unrealised_pnl': float(positions.unrealised_pnl),
                'size': float(positions.size)
            }
            return pos
        except GateApiException as e:
            print(f'Error [get_position]: {e}')
            return {'entry_price': 0.0, 'unrealised_pnl': 0.0, 'size': 0.0}
    
    @staticmethod
    def open_order(coin: str, sd: str, amount_usdt: int, reduceOnly: bool):
        try:
            c = f'{coin[:-4]}_{coin[-4:]}'
            
            contract = GT.futures_api.get_futures_contract('usdt', c)
            mark_price_round = float(contract.mark_price_round)
            quanto_multiplier = float(contract.quanto_multiplier)
            order_size_min = float(contract.order_size_min)
            last_price=float(contract.last_price)
            close = False
            size = (amount_usdt / last_price) // quanto_multiplier
            if sd == 'Sell':
                size = 0-size
            if reduceOnly:
                size = 0
                close = True
            order = FuturesOrder(contract=c, size=size, price='0', tif='ioc', close=close)
            order_response = GT.futures_api.create_futures_order('usdt', order)
            return order_response.id, last_price
        except GateApiException as e:
            print(f'Error [get_balance]: {e}')
            return 0, 0
        
    @staticmethod
    def open_SL(coin: str, sd: str, amount_coins: float, open_price: float, SL_perc: float) -> str:
        try:
            c = f'{coin[:-4]}_{coin[-4:]}'
            contract = GT.futures_api.get_futures_contract('usdt', c)
            mark_price_round = float(contract.mark_price_round)
            price = 0
            if sd == 'Buy':
                price = open_price * (1-SL_perc)
            elif sd == 'Sell':
                price = open_price * (1+SL_perc)
            price = round_price(price, mark_price_round)
            triger_price = price * (1 + 0.001) if sd == 'Sell' else price * (1 - 0.001)
            order_type = 'plan-close-long-position' if sd == 'Buy' else 'plan-close-short-position'
            rule = 2 if sd == 'Buy' else 1
            initial = FuturesInitialOrder(contract=c, size=0, price=str(0), close=True, tif='ioc', is_close=True)
            trigger = FuturesPriceTrigger(strategy_type=0, price_type=2, price=str(round_price(triger_price, mark_price_round)), rule=rule)
            
            print(order_type)
            order = FuturesPriceTriggeredOrder(initial=initial, trigger=trigger, order_type=order_type)
            order_response = GT.futures_api.create_price_triggered_order('usdt', order)
            print(order_response)
            return order_response.id
        except GateApiException as e:
            print(f'Error: {e}')
            return 0, 0