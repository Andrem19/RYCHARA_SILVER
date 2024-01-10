from kucoin_futures.client import Trade
from kucoin_futures.client import Market
from kucoin_futures.client import User
from models.settings import Settings
from decouple import config
import threading
import math

round_coins = {
    'ADAUSDT': 5,
    'FTMUSDT': 4,
    'HBARUSDT': 5,
    'ARBUSDT': 4,
    'AAVEUSDT': 2,
    'EOSUSDT': 4,
    'EGLDUSDT': 2,
    'FLOWUSDT': 4,
    'KLAYUSDT': 4,
    'FXSUSDT': 3,
    'MINAUSDT': 4,
    'CRVUSDT': 4,
    'DASHUSDT': 2,
    'ALGOUSDT': 4,
    'DOTUSDT': 3,
    'FILUSDT': 3,
    'GALAUSDT': 5,
    'XRPUSDT': 4,
    'VETUSDT': 5,
    'MATICUSDT': 4,
    'FTMUSDT': 4,
    'KAVAUSDT': 4,
    'MANAUSDT': 4,
    'ATOMUSDT': 3,
    'ADAUSDT': 5,
    'FLOWUSDT': 4,
    'AXSUSDT': 3,
    'SOLUSDT': 3,
    'INJUSDT': 3,
    'EGLDUSDT': 2,
    'GRTUSDT': 5,
    'DOGEUSDT': 5,
    'SNXUSDT': 3,
    'APTUSDT': 3,
    'NEOUSDT': 3,
    'SUIUSDT': 4,
    'MINAUSDT': 4,
    'RNDRUSDT': 4,
    'XMRUSDT': 2,
    'TRXUSDT': 5,
    'UNIUSDT': 3,
    'LTCUSDT': 2,
    'AAVEUSDT': 2,
    'XLMUSDT': 5,
    'AVAXUSDT': 2,
    'STXUSDT': 4,
    'SANDUSDT': 5,
    'THETAUSDT': 4,
    'APEUSDT': 3,
    'DYDXUSDT': 3,
    'IOTAUSDT': 5,
    'LINKUSDT': 3,
    'OPUSDT': 4,
    'QNTUSDT': 2,
}

amount_lot = {
    'ADAUSDT': 10,
    'FTMUSDT': 1,
    'HBARUSDT': 10,
    'ARBUSDT': 1,
    'AAVEUSDT': 0.01,
    'EOSUSDT': 1,
    'EGLDUSDT': 0.01,
    'FLOWUSDT': 0.1,
    'KLAYUSDT': 1,
    'FXSUSDT': 0.1,
    'MINAUSDT': 1,
    'CRVUSDT': 1,
    'DASHUSDT': 0.01,
    'ALGOUSDT': 1,
    'DOTUSDT': 1,
    'FILUSDT': 0.1,
    'GALAUSDT': 1,
    'XRPUSDT': 10,
    'VETUSDT': 100,
    'MATICUSDT': 10,
    'FTMUSDT': 1,
    'KAVAUSDT': 0.1,
    'MANAUSDT': 1,
    'ATOMUSDT': 1,
    'ADAUSDT': 10,
    'FLOWUSDT': 0.1,
    'AXSUSDT': 0.1,
    'SOLUSDT': 0.1,
    'INJUSDT': 1,
    'EGLDUSDT': 0.01,
    'GRTUSDT': 1,
    'DOGEUSDT': 100,
    'SNXUSDT': 0.1,
    'APTUSDT': 0.1,
    'NEOUSDT': 0.1,
    'SUIUSDT': 1,
    'MINAUSDT': 1,
    'RNDRUSDT': 1,
    'XMRUSDT': 0.01,
    'TRXUSDT': 100,
    'UNIUSDT': 1,
    'LTCUSDT': 0.1,
    'AAVEUSDT': 0.01,
    'XLMUSDT': 10,
    'AVAXUSDT': 0.1,
    'STXUSDT': 1,
    'SANDUSDT': 1,
    'THETAUSDT': 0.1,
    'APEUSDT': 0.1,
    'DYDXUSDT': 0.1,
    'IOTAUSDT': 10,
    'LINKUSDT': 0.1,
    'OPUSDT': 1,
    'QNTUSDT': 0.01,
}

def round_price(price, tick_size):
    precision = int(round(-math.log(tick_size, 10)))
    return round(price, precision)

class KuCoin:

    @staticmethod
    def open_limit_order(coin: str, sd: str, amount_usdt: int):
        try:
            curent_price = KuCoin.get_last_price(coin)
            contract_info = KuCoin.market_client.get_contract_detail(f'{coin}M')
            lot = (amount_usdt / curent_price) // contract_info['multiplier']
        
            side = 'buy' if sd == 'Buy' else 'sell'

            pr = 0
            if side == 'buy':
                pr = curent_price * (1+0.0001)
            else:
                pr = curent_price * (1-0.0001)
            if lot < 1:
                lot = 1
            price = round_price(pr, contract_info['tickSize'])
            order_id = KuCoin.client.create_limit_order(symbol=f'{coin}M', side=side, lever='10', size=int(lot), price=price)
            return order_id['orderId'], pr
        except Exception as e:
            print(f'Error [open_limit_order]: {e}')
            return 0, 0
    
    @staticmethod
    def open_market_order(coin: str, sd: str, amount_usdt: int) -> str:
        try:
            curent_price = KuCoin.get_last_price(coin)
            lot = (amount_usdt / curent_price) // amount_lot[coin]
            side = 'buy' if sd == 'Buy' else 'sell'
            order_id = KuCoin.client.create_market_order(symbol=f'{coin}M', side=side, lever='10', size=int(lot), closeOrder=False)
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

            order_id = KuCoin.client.create_limit_order(symbol=f'{coin}M', side=side, size=amount_lot, lever='10', closeOrder=True, stopPriceType='IP', price=round(price, round_coins[coin]), stopPrice=round(price, round_coins[coin]), stop=st)
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
            
            order_id = KuCoin.client.create_limit_order(symbol=f'{coin}M', side=side, size=amount_lot, lever='10', closeOrder=True, stopPriceType='TP', price=round(price, round_coins[coin]), stopPrice=round(price, round_coins[coin]), stop=st)
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