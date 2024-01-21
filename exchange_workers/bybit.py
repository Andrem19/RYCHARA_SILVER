from decouple import config
from models.settings import Settings
import threading
import time
import shared_vars as sv
from models.settings import Settings
import time
import uuid
import hashlib
import traceback
import requests
import threading
import hmac
import math
import json

def round_price(price, tick_size):
    precision = int(round(-math.log(tick_size, 10)))
    return round(price, precision)

class BB:

    api_key = None
    secret_key = None
    httpClient = None
    recv_window = None
    url = None
    init_lock = threading.Lock()

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if BB.httpClient is not None:
                return
        
        # Acquire the lock to ensure only one thread initializes the variables
        with BB.init_lock:
            # Check again after acquiring the lock in case another thread has already initialized the variables
            if BB.httpClient is not None:
                return
            
            BB.api_key = config(settings.API_KEY)
            BB.secret_key = config(settings.SECRET_KEY)
            BB.httpClient = requests.Session()
            BB.recv_window = str(5000)
            BB.url = "https://api.bybit.com"


    @staticmethod
    def is_contract_exist(coin:str)-> (bool, list):
        try:
            response = requests.get('https://api.bybit.com/v5/market/instruments-info?category=linear')
            data = json.loads(response.text)
            symbols = []
            for contract in data['result']['list']:
                symbols.append(contract['symbol'])
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist] {e}')

    @staticmethod
    def HTTP_Request(endPoint, method, payload, Info):
        global time_stamp
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = BB.genSignature(payload)
        headers = {
            'X-BAPI-API-KEY': BB.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': BB.recv_window,
            'Content-Type': 'application/json'
        }
        if(method == "POST"):
            response = BB.httpClient.request(method, BB.url + endPoint, headers=headers, data=payload)
        else:
            response = BB.httpClient.request(method, BB.url + endPoint + "?" + payload, headers=headers)
        # print(Info + " Elapsed Time: " + str(response.elapsed))
        return response.text
        
    
    @staticmethod
    def genSignature(payload):
        param_str = str(time_stamp) + BB.api_key + BB.recv_window + payload
        hash = hmac.new(bytes(BB.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    @staticmethod
    def get_balance(coin: str):
        endpoint = '/v5/account/wallet-balance'
        payload = 'accountType=UNIFIED&coin=' + coin
        method = 'GET'
        try:
            result = BB.HTTP_Request(endpoint, method, payload, "get_position")
            data = json.loads(result)
            if 'result' in data and 'list' in data['result'] and len(data['result']['list']) > 0:
                wallet_info = data['result']['list'][0]
                return float(wallet_info['totalEquity'])
            else:
                return None
        except Exception as e:
            print(f"Error [get_balance]: {e}")
            print(traceback.format_exc())
            return None
    
    @staticmethod
    def get_last_price(symbol):
        try:
            url = f"{BB.url}/v5/market/tickers?category=inverse&symbol=" + symbol
            response = requests.get(url).json()
            
            if response["retCode"] == 0:
                if len(response["result"]["list"]) > 0:
                    return float(response["result"]["list"][0]["lastPrice"])
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error [get_last_price]: {e}")
            return None
        
    @staticmethod
    def get_position(symbol: str) -> dict | None:
        endpoint = f'/v5/position/list'
        payload = 'category=linear&symbol=' + symbol
        method = 'GET'
        try:
            result = BB.HTTP_Request(endpoint, method, payload, "get_position")
            data = json.loads(result)
            
            if 'result' in data and 'list' in data['result'] and len(data['result']['list']) > 0:
                position_info = data['result']['list'][0]
                return position_info
            else:
                return None
        except Exception as e:
            print(f"Error [get_position]: {e}")
            return None
        
    @staticmethod
    def instrument_info(symbol: str) -> dict:
        try:
            endpoint = f'/v5/market/instruments-info'
            payload = 'category=linear&symbol=' + symbol
            method = 'GET'

            instrument = {}
            result = BB.HTTP_Request(endpoint, method, payload, "get_position")
            data = json.loads(result)
            if data['retCode'] == 0:
                inst = data['result']['list'][0]
                instrument['priceScale'] = inst['priceScale']
                instrument['qtyStep'] = inst['lotSizeFilter']['qtyStep']
                return instrument
            else:
                return None
        except Exception as e:
            print(f"Error [instrument_info]: {e}")
            return None
        
    @staticmethod
    def cancel_orders(symbol):
        try:
            cancel_type = "Cancel all"
            endpoint="/v5/order/cancel-all"
            method="POST"

            pr= {
                "category":"linear",
                "symbol": symbol,
                }
            params = json.dumps(pr)

            result = BB.HTTP_Request(endpoint,method,params,cancel_type)
            data = json.loads(result)
            print(data)
        except Exception as e:
            print(f"Error [cancel_orders]: {e}")
            return None

    @staticmethod
    def open_order(ordType: str, coin: str, sd: str, amount_usdt: int, reduceOnly: bool):
        try:
            endpoint = "/v5/order/create"
            method = "POST"
            acc = BB.instrument_info(coin)
            priceScale=int(acc['priceScale'])
            qtyStep=float(acc['qtyStep'])
            last_price = BB.get_last_price(coin)
            oType = 'Market' if ordType == 'market' else 'Limit'

            size = amount_usdt / last_price
            if size % qtyStep != 0:
                size = size - (size % qtyStep)
            side = sd
            pr = 0
            if sd == 'Buy':
                pr = last_price * (1+0.0001)
            else:
                pr = last_price * (1-0.0001)
            if reduceOnly:
                size = 0
                side = 'Buy' if side == 'Sell' else 'Sell'
            sz = round_price(size, qtyStep)
            params = {
                "category": "linear",
                "symbol": coin,
                "side": side,
                "positionIdx": 0,
                "orderType": oType,
                "qty": str(sz),
                "isLeverage": 10,
                "timeInForce": "GTC",
                "price": str(round(pr, priceScale)),
                "reduceOnly": reduceOnly
            }

            params_str = json.dumps(params)
            print(params_str)
            order = BB.HTTP_Request(endpoint, method, params_str, f"create_{ordType}_order")
            print(order)
            data = json.loads(order)
            return data['result']['orderId'], pr
        except Exception as e:
            print(f'Error [open_order]: {e}')
            return 0
        
    
    @staticmethod
    def open_SL(ordType: str, coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
        try:
            endpoint = '/v5/position/trading-stop'
            method = 'POST'

            acc = BB.instrument_info(coin)
            priceScale=int(acc['priceScale'])
            oType = 'Market' if ordType == 'market' else 'Limit'
            side = 'Buy' if sd == 'Sell' else 'Buy'

            price = 0
            if sd == 'Buy':
                price = open_price * (1-SL_perc)
            elif sd == 'Sell':
                price = open_price * (1+SL_perc)

            executive_price = price * (1 + 0.001) if side == 'Sell' else price * (1 - 0.001)

            params = {
                "category":"linear",
                "symbol": coin,
                "slTriggerBy": "LastPrice",
                "tpslMode": "Partial",
                "slOrderType": oType,
                "slSize": str(amount_lot),
                "positionIdx": 0,
                "stopLoss": str(round(price, priceScale)),
            }
            if oType == 'Limit':
                params['slLimitPrice'] = str(round(executive_price, priceScale))

            params_str = json.dumps(params)

            result = BB.HTTP_Request(endpoint, method, params_str, f"Add {oType} Stop-Loss")
            data = json.loads(result)
            return 0
        except Exception as e:
            print(f'Error [open_SL]: {e}')
            return 0
        
    
