from bingX.perpetual.v2 import Perpetual
from bingX import ClientError
# from bingX.standard import Standard
from models.settings import Settings
from decouple import config
import threading
from datetime import datetime
import traceback

class BX:

    client: Perpetual = None
    # standart: Standard = None
    init_lock = threading.Lock()

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if BX.client is not None:
                return
        
        # Acquire the lock to ensure only one thread initializes the variables
        with BX.init_lock:
            # Check again after acquiring the lock in case another thread has already initialized the variables
            if BX.client is not None:
                return
            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            # Set the variables from shared_vars module
            BX.client = Perpetual(api_key, secret_key)
            # BX.standard = Standard(api_key, secret_key)
    
    @staticmethod
    def re_init(settings: Settings):
        BX.client = None
        BX.init(settings)
    
    @staticmethod
    def get_last_price(coin: str):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            tick = BX.client.ticker(c)
            return float(tick['lastPrice'])
        except Exception as e:
            print(f'Error [get_last_price]: {e}')
            return 0
        
    # @staticmethod
    # def switch_lev():
    #     import time
    #     import requests
    #     import hmac
    #     from hashlib import sha256
    #     api_key = config('BXAPI_1')
    #     secret_key = config('BXSECRET_1')
    #     APIURL = "https://open-api.bingx.com"
    #     APIKEY = api_key
    #     SECRETKEY = secret_key

    #     def demo():
    #         payload = {}
    #         path = '/openApi/swap/v2/trade/leverage'
    #         method = "POST"
    #         paramsMap = {
    #         "leverage": "20",
    #         "side": "SHORT",
    #         "symbol": "ZIL-USDT",
    #         "timestamp": str(int(time.time() * 1000))
    #     }
    #         paramsStr = praseParam(paramsMap)
    #         return send_request(method, path, paramsStr, payload)

    #     def get_sign(api_secret, payload):
    #         signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    #         print("sign=" + signature)
    #         return signature


    #     def send_request(method, path, urlpa, payload):
    #         url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
    #         print(url)
    #         headers = {
    #             'X-BX-APIKEY': APIKEY,
    #         }
    #         response = requests.request(method, url, headers=headers, data=payload)
    #         return response.text

    #     def praseParam(paramsMap):
    #         sortedKeys = sorted(paramsMap)
    #         paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    #         return paramsStr+"&timestamp="+str(int(time.time() * 1000))
        
    #     return demo()
        
    
    @staticmethod
    def get_position(coin: str):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            positions = BX.client.positions(c)
            if len(positions)> 0:
                return positions[0]
            else:
                return None
        except Exception as e:
            print(f'Error [get_position]: {e}')
            return 0
    
    @staticmethod
    def get_balance() -> float:
        try:
            acc = BX.client.balance()
            return acc['balance']['balance']
        except Exception as e:
            print(f'Error [get_balance]: {e}')
            return 0
    
    @staticmethod
    def cancel_all_orders(coin: str) -> str:
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            res = BX.client.cancel_all_orders(symbol=c)
        except ClientError as e:
            # Вывод информации об ошибке
            print(f"Code: {e.error_code}")
            print(f"Msg [cancel_all_orders]: {e.error_msg}")
    @staticmethod
    def is_contract_exist(coin:str)-> (bool, list):
        try:
            symbols = []
            contracts = BX.client.contracts()
            for cont in contracts:
                s = f'{cont["symbol"][:-5]}{cont["symbol"][-4:]}'
                symbols.append(s)
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist] {e}')

    @staticmethod
    def open_order(ordType: str, coin: str, sd: str, amount_usdt: int, reduceOnly: bool, coin_amount = 0):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            quantityPrecision = 0
            pricePrecision = 0
            size_tick = 0
            contracts = BX.client.contracts()
            for cont in contracts:
                if cont['symbol'] == c:
                    quantityPrecision = cont['quantityPrecision']
                    pricePrecision = cont['pricePrecision']
                    size_tick = cont['size']
                    break
            curent_price = BX.get_last_price(coin)
            lev = BX.client.leverage(c)
            print(lev)
            minLeverage = min([lev['maxLongLeverage'], lev['maxShortLeverage']])
            leverage = 20 if minLeverage >= 20 else minLeverage
            side = 'BUY' if sd == 'Buy' else 'SELL'
            positionSide = 'BOTH'
            # lev_side = 'LONG' if sd == 'Buy' else 'SHORT'
            size = round(amount_usdt / curent_price, quantityPrecision)
            pr = 0
            if side == 'BUY':
                pr = round(curent_price * (1+0.0001), pricePrecision)
            else:
                pr = round(curent_price * (1-0.0001), pricePrecision)
            if reduceOnly == True:
                side = 'SELL' if side == 'BUY' else 'BUY'
                size = coin_amount
            BX.client.switch_leverage(symbol=c, side='BOTH', leverage=f'{leverage}')
            order_info = BX.client.trade_order(
                symbol=c,
                type='MARKET',
                side=side,
                positionSide=positionSide,
                price=pr,
                quantity=size,
            )
            return order_info['order']['orderId'], order_info['order']['price']

        except ClientError as e:
            # Вывод информации об ошибке
            print(f"open_order Code: {e.error_code}")
            print(f"Msg [open_order]: {e.error_msg}")
            return 0, 0

    @staticmethod
    def open_SL(ordType: str, coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            side = 'BUY' if sd == 'Sell' else 'SELL'

            quantityPrecision = 0
            pricePrecision = 0
            size_tick = 0
            contracts = BX.client.contracts()
            for cont in contracts:
                if cont['symbol'] == c:
                    quantityPrecision = cont['quantityPrecision']
                    pricePrecision = cont['pricePrecision']
                    size_tick = cont['size']
                    break

            price = 0
            if side == 'BUY':
                price = round(open_price * (1+SL_perc), pricePrecision)
            elif side == 'SELL':
                price = round(open_price * (1-SL_perc), pricePrecision)
            
            st_price = price * (1-0.0001) if side == 'SELL' else price * (1+0.0001)
            stop_type = 'STOP' if ordType =='limit' else 'STOP_MARKET'
            order_info = BX.client.trade_order(
                symbol=c,
                type=stop_type,
                side=side,
                positionSide='BOTH',
                price=price,
                stopPrice=round(st_price, pricePrecision),
                quantity=amount_lot,
            )
            return order_info['order']['orderId']
        
        except ClientError as e:
            # Вывод информации об ошибке
            print(f"open_SL Code: {e.error_code}")
            print(f"Msg [open_SL]: {e.error_msg}")
            return 0