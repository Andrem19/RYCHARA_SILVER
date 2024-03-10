from pyxt.perp import Perp
from models.settings import Settings
from decouple import config
import threading
import math
from datetime import datetime

def round_price(price, tick_size):
    precision = int(round(-math.log(tick_size, 10)))
    return round(price, precision)

def convert_name(name: str):
    res = name.split('_')
    return f'{res[0].upper()}{res[1].upper()}'

class XT:

    client: Perp = None
    # standart: Standard = None
    init_lock = threading.Lock()

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if XT.client is not None:
                return
        
        # Acquire the lock to ensure only one thread initializes the variables
        with XT.init_lock:
            # Check again after acquiring the lock in case another thread has already initialized the variables
            if XT.client is not None:
                return
            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            XT.client = Perp('https://fapi.xt.com', api_key, secret_key)


    @staticmethod
    def get_instrument_info(coin: str):
        try:
            c = f'{coin[:-4]}_{coin[-4:]}'
            _, data, _ = XT.client.get_market_config(c)
            return data['result'] ##'contractSize': '10', 'initLeverage': 50, 'initPositionType': 'CROSSED', 'baseCoinPrecision': 8, 'baseCoinDisplayPrecision': 4, 'quoteCoinPrecision': 8, 'quoteCoinDisplayPrecision': 4, 'quantityPrecision': 0, 'pricePrecision': 4,
        except Exception as e:
            print(f'Error: [is_contract_exist {datetime.now()}] {e}')
    
    @staticmethod
    def is_contract_exist(coin: str):
        try:
            symbols = []
            url = 'https://fapi.xt.com/future/market/v3/public/symbol/list'
            _, data, _ = XT.client._fetch(method="GET", url=url, params={})

            if 'result' in data:
                if 'symbols' in data['result']:
                    for contract in data['result']['symbols']:
                        parts = contract['symbol'].split('_')
                        coin = f'{parts[0].upper()}{parts[1].upper()}'
                        symbols.append(coin)

            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist {datetime.now()}] {e}')
    
    @staticmethod
    def get_balance() -> float:
        try:
            _, result, _ = XT.client.get_account_capital()
            for bal in result['result']:
                if bal['coin']=='usdt':
                    return float(bal['walletBalance'])
        except Exception as e:
            print(f'Error [get_balance {datetime.now()}]: {e}')
            return 0

    @staticmethod
    def get_last_price(coin):
        try:
            c = f'{coin[:-4].lower()}_{coin[-4:].lower()}'
            _, last_pr, _ = XT.client.get_book_ticker(c)
            if 'result' in last_pr:
                return float(last_pr['result']['ap'])
            return 0
        except Exception as e:
            print(f'Error [get_last_price {datetime.now()}]: {e}')
            return 0

    @staticmethod
    def get_position(coin: str, sg: str) -> dict | None:
        side = 'LONG' if sg == 1 else 'SHORT'
        try:
            c = f'{coin[:-4].lower()}_{coin[-4:].lower()}'
            bodymod = "application/x-www-form-urlencoded"
            path = "/future/user" + '/v1/position/list'
            url = XT.client.host + path
            params = {}
            api_key = config('XTAPI_1')
            api_secret = config('XTSECRET_1')
            header = XT.client._create_sign(api_key, api_secret, path=path, bodymod=bodymod, params=params)
            header["Content-Type"] = "application/x-www-form-urlencoded"
            code, result, error = XT.client._fetch(method="GET", url=url, headers=header, params=params, timeout=XT.client.timeout)
            print(result)
            if 'result' in result:
                if len(result['result'])> 0:
                    for pos in result['result']:
                        if pos['symbol']==c and pos['positionSide']==side:
                            return pos
            return None

        except Exception as e:
            print(f'[get_position]: {e}')
            return 0

    @staticmethod
    def is_any_position_exists():
        try:
            position_list = []
            bodymod = "application/x-www-form-urlencoded"
            path = "/future/user" + '/v1/position/list'
            url = XT.client.host + path
            params = {}
            api_key = config('XTAPI_1')
            api_secret = config('XTSECRET_1')
            header = XT.client._create_sign(api_key, api_secret, path=path, bodymod=bodymod, params=params)
            header["Content-Type"] = "application/x-www-form-urlencoded"
            code, result, error = XT.client._fetch(method="GET", url=url, headers=header, params=params, timeout=XT.client.timeout)
            if 'result' in result:
                if len(result['result'])> 0:
                    for pos in result['result']:
                        if float(pos['positionSize']) != 0:
                            sd = 'Buy' if pos['positionSide']== 'LONG' else 'Sell'
                            amt = float(pos['positionSize'])
                            name = convert_name(pos['symbol'])
                            inst = [name, sd, amt]
                            position_list.append(inst)
            return position_list
        except Exception as e:
            print(f'Error [is_any_position_exists]: {e}')
            return [1]
        
    @staticmethod
    def cancel_all_orders(coin: str):
        try:
            c = f'{coin[:-4].lower()}_{coin[-4:].lower()}'
            _, res, _ = XT.client.cancel_all_order(c)
            print(res)
        except Exception as e:
            print(f'Error [cancel_all_orders]: {e}')
            return [1]
        
    @staticmethod
    def open_market_order(coin: str, sd: str, amount_usdt: int, reduceOnly: bool, amount_coins = 0):
        try:
            c = f'{coin[:-4].lower()}_{coin[-4:].lower()}'
            last_price = XT.get_last_price(coin)
            inst_info = XT.get_instrument_info(coin)
            size = int((amount_usdt / last_price) // float(inst_info['contractSize']))
            init_lever = int(inst_info['initLeverage'])
            if init_lever<20:
                pass
            if size < 1:
                size = 1
            side = 'BUY' if sd == 'Buy' else 'SELL'
            position_side = 'LONG' if sd == 'Buy' else 'SHORT'
            params = {
                "orderSide": side,
                "orderType": 'MARKET',
                "origQty": size,
                "positionSide": position_side,
                "symbol": c
            }
            if reduceOnly:
                params['reduceOnly'] = 'true'
                params['origQty'] = amount_coins
                params['orderSide'] = 'SELL' if sd == 'Buy' else 'BUY'
            print(params)
            order = XT.send_order('/future/trade/v1/order/create', params)
            if 'result' in order:
                return order['result'], last_price
            else:
                return 0, last_price
        except Exception as e:
            print(f'Error [open_market_order]: {e}')
            return 0,0
        
    @staticmethod
    def open_SL(coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
        try:
            c = f'{coin[:-4].lower()}_{coin[-4:].lower()}'
            inst_info = XT.get_instrument_info(coin)
            price_precision = int(inst_info['pricePrecision'])
            # qnPrec = int(inst_info['quantityPrecision'])
            print(f'pr prec: {price_precision}')
            position_side = 'LONG' if sd == 'Buy' else 'SHORT'
            # side = 'SELL' if sd == 'Buy' else 'BUY'
            price = 0
            if sd == 'Buy':
                price = open_price * (1-SL_perc)
            elif sd == 'Sell':
                price = open_price * (1+SL_perc)
            print(price)
            price = round(price, price_precision)
            print(price)
            # executive_price = price * (1 + 0.001) if side == 'Sell' else price * (1 - 0.001)
            # executive_price = round_price(executive_price, price_precision)
            expireTime = datetime.now().timestamp() + 1200
            params = {
                "positionSide": position_side,
                "origQty": amount_lot,
                'expireTime': int(expireTime),
                "triggerStopPrice": price,
                "symbol": c
            }
            print(params)
            order = XT.send_order('/future/trade/v1/entrust/create-profit', params)
            print(order)
            # if 'result' in order:
            #     return order['result']
            # else:
            #     return 0
        except Exception as e:
            print(f'Error [open_SL]: {e}')
            return 0
        
    @staticmethod
    def send_order(endpoint: str, params: dict):
        try:
            api_key = config('XTAPI_1')
            api_secret = config('XTSECRET_1')
            bodymod = "application/json"
            url = XT.client.host + endpoint
            params = dict(sorted(params.items(), key=lambda e: e[0]))
            header = XT.client._create_sign(api_key, api_secret, path=endpoint, bodymod=bodymod,
                                    params=params)
            code, success, error = XT.client._fetch(method="POST", url=url, headers=header, data=params, timeout=XT.client.timeout)
            return success
        except Exception as e:
            print(f'Error [send_order]: {e}')
            return 0