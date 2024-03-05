from decouple import config
# import okx.Account as Account
# import okx.Account as Account
# import okx.Trade as Trade
from okx.Trade import TradeAPI
from okx.Account import AccountAPI
from okx.PublicData import PublicAPI
from models.settings import Settings
import okx.MarketData as MarketData
import threading
import helpers.services as serv
import requests
from datetime import datetime
import math

def convert_name(name: str):
    res = name.split('-')
    coin = f'{res[0]}{res[1]}'
    print(coin)
    return coin

def round_price(price, tick_size):
    precision = int(round(-math.log(tick_size, 10)))
    return round(price, precision)

class OKX:

    futuresAPI: TradeAPI = None
    accountAPI: AccountAPI = None
    publicDataAPI: PublicAPI = None
    init_lock = threading.Lock()

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if OKX.futuresAPI is not None and OKX.accountAPI is not None and OKX.publicDataAPI is not None:
                return
        
        # Acquire the lock to ensure only one thread initializes the variables
        with OKX.init_lock:
            # Check again after acquiring the lock in case another thread has already initialized the variables
            if OKX.futuresAPI is not None and OKX.accountAPI is not None and OKX.publicDataAPI is not None:
                return
            api_key = config(settings.API_KEY)
            secret_key = config(settings.SECRET_KEY)
            passphrase = 'Passphrase19*'
            # Set the variables from shared_vars module
            OKX.accountAPI = AccountAPI(api_key, secret_key, passphrase, False, '0', debug=False)
            OKX.futuresAPI = TradeAPI(api_key, secret_key, passphrase, False, '0', debug=False)
            OKX.publicDataAPI = PublicAPI(api_key, secret_key, passphrase, False, '0', debug=False)


    @staticmethod
    def re_init(settings: Settings):
        OKX.accountAPI = None
        OKX.futuresAPI = None
        OKX.publicDataAPI = None
        OKX.init(settings)

    @staticmethod
    def is_contract_exist(coin:str)-> (bool, list):
        try:
            data = OKX.publicDataAPI.get_instruments('SWAP')

            symbols = []
            if 'data' in data:
                for contract in data['data']:
                    parts = contract['instId'].split('-')
                    s = parts[0] + parts[1]
                    symbols.append(s)
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist {datetime.now()}] {e}')
    
    @staticmethod
    def get_instrument_info(coin: str):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}-SWAP'
            responce = requests.get(f'https://www.okx.com/api/v5/public/instruments?instType=SWAP&instId={c}')
            data = responce.json()
            if len(data)> 0:
                return data['data'][0]
            else:
                raise Exception(f'no instrument {c}')
        except Exception as e:
            print(f'Error [open_order {datetime.now()}]: {e}')
            return 0, 0
        
    @staticmethod
    def open_SL(coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            side = 'buy' if sd == 'Sell' else 'sell'
            price = 0
            if side == 'buy':
                price = open_price * (1+SL_perc)
            elif side == 'sell':
                price = open_price * (1-SL_perc)

            res = OKX.futuresAPI.place_algo_order(
                instId=f'{c}-SWAP',
                tdMode="cross",
                side=side,
                ordType="conditional",
                sz=abs(amount_lot),
                slTriggerPx=price,
                slOrdPx=price * (1 - 0.001) if side == 'sell' else price * (1 + 0.001)
            )
            print(res)
            order_id = 0
            if 'data' in res:
                if len(res['data']) > 0:
                    order_id = res['data'][0]['algoId']
                    return order_id
            else:
                raise Exception(f'Somthing went wrong. orderSL didnt placed: {res}')
        except Exception as e:
            print(f'Error [open_SL {datetime.now()}]: {e}')
            return 0

    @staticmethod
    def open_order(ordType: str, coin: str, sd: str, amount_usdt: int, reduceOnly: bool):
        try:
            side = 'buy' if sd == 'Buy' else 'sell'
            inst_info = OKX.get_instrument_info(coin)
            contract_val = float(inst_info['ctVal'])
            tik_size = float(inst_info['tickSz'])
            max_lever = int(inst_info['lever'])
            c = f'{coin[:-4]}-{coin[-4:]}'
            last_price = OKX.get_last_price(coin)
            lev = 20 if max_lever >= 20 else max_lever
            OKX.accountAPI.set_leverage(lever=f'{lev}', mgnMode='cross', instId=f'{c}-SWAP', ccy='USDT')
            pr = 0
            if side == 'buy':
                pr = last_price * (1+0.0001)
            else:
                pr = last_price * (1-0.0001)
            lot = (amount_usdt / last_price) // contract_val
            if reduceOnly == True:
                side = 'sell' if sd == 'Buy' else 'buy'
                lot = lot*2
            if lot < 1:
                lot = 1
                pr = round_price(pr, tik_size)
            res = OKX.futuresAPI.place_order(instId=f'{c}-SWAP', tdMode='cross', side=side, ordType=ordType, sz=lot, px=pr, ccy='USDT', reduceOnly=reduceOnly) #isolated

            order_id = res['data'][0]['ordId']
            return order_id, pr
        except Exception as e:
            print(f'Error [open_order {datetime.now()}]: {e}')
            return 0, 0

    
    @staticmethod
    def open_order_with_sl(ordType: str, coin: str, sd: str, amount_usdt: int, SL_perc: float, TP_perc: float = 0) -> str:
        try:
            side = 'buy' if sd == 'Buy' else 'sell'
            inst_info = OKX.get_instrument_info(coin)
            contract_val = float(inst_info['ctVal'])
            tik_size = float(inst_info['tickSz'])
            c = f'{coin[:-4]}-{coin[-4:]}'
            last_price = OKX.get_last_price(coin)
            pr = 0
            if side == 'buy':
                pr = last_price * (1+0.0001)
            else:
                pr = last_price * (1-0.0001)
            lot = (amount_usdt / last_price) // contract_val
            
            if side == 'sell':
                price_sl = pr * (1+SL_perc)
            elif side == 'buy':
                price_sl = pr * (1-SL_perc)
        
            slOrdPx = price_sl * (1 - 0.001) if side == 'buy' else price_sl * (1 + 0.001)

            # if side == 'sell':
            #     price_tp = pr * (1-TP_perc)
            # elif side == 'buy':
            #     price_tp = pr * (1+TP_perc)
        
            # tpOrdPx = price_tp * (1 + 0.001) if side == 'buy' else price_tp * (1 - 0.001)
            pr = round_price(pr, tik_size)
            res = OKX.futuresAPI.place_order(instId=f'{c}-SWAP', tdMode='cross', side=side, ordType=ordType, sz=lot, px=pr, ccy='USDT', slTriggerPx=price_sl, slOrdPx=slOrdPx) #isolated

            order_id = res['data'][0]['ordId']
            return order_id, pr
        except Exception as e:
            print(f'Error [open_order_with_sl {datetime.now()}]: {e}')
            return 0, 0
    
    @staticmethod
    def cancel_order(coin: str, ordId: str) -> str:
        c = f'{coin[:-4]}-{coin[-4:]}'
        try:
            result = OKX.futuresAPI.cancel_order(instId=f'{c}-SWAP', ordId=ordId)
        except Exception as e:
            print(f'Error [cancel_order]: {e}')
    
    @staticmethod
    def cancel_all_orders(coin: str) -> str:
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            result = OKX.futuresAPI.get_order_list(instType="SWAP", instId=f'{c}-SWAP')
            print(result)
            if 'data' in result:
                print(1)
                for i in range(len(result['data'])):
                    res = OKX.futuresAPI.cancel_order(instId=f'{c}-SWAP', ordId=result['data'][i]['ordId'])
        except Exception as e:
            print(f'Error [cancel_all_orders {datetime.now()}]: {e}')
    
    @staticmethod
    def cancel_algo_order(coin: str, ordId: str) -> str:
        c = f'{coin[:-4]}-{coin[-4:]}'
        try:
            algo_orders = [
                {"instId": f'{c}-SWAP', "algoId": ordId},
            ]
            result = OKX.futuresAPI.cancel_algo_order(algo_orders)
        except Exception as e:
            print(f'Error [cancel_algo_order {datetime.now()}]: {e}')
    
    @staticmethod
    def cancel_all_algo_orders(coin: str) -> str:
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            result = OKX.futuresAPI.order_algos_list(ordType="conditional", instId=f'{c}-SWAP')
            print(result)
            if 'data' in result:
                print(1)
                for i in range(len(result['data'])):
                    algo_orders = [
                        {"instId": f'{c}-SWAP', "algoId": result['data'][i]['algoId']},
                    ]
                    res = OKX.futuresAPI.cancel_algo_order(algo_orders)
        except Exception as e:
            print(f'Error [cancel_all_algo_orders {datetime.now()}]: {e}')
    
    @staticmethod
    def open_TP(coin: str, sd: str, amount_lot: str, open_price: float, TP_perc: float):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            side = 'buy' if sd == 'Sell' else 'sell'
            price = 0
            if side == 'buy':
                price = open_price * (1-TP_perc)
            elif side == 'sell':
                price = open_price * (1+TP_perc)
            amount_lot = amount_lot*2
            res = OKX.futuresAPI.place_order(instId=f'{c}-SWAP', tdMode='cross', side=side, ordType='limit', sz=amount_lot, px=price, ccy='USDT', reduceOnly=True) #isolated
            order_id = res['data'][0]['ordId']
            return order_id
        except Exception as e:
            print(f'Error [open_TP {datetime.now()}]: {e}')
            return 0
    
    @staticmethod
    def get_position(coin: str):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            position = OKX.accountAPI.get_positions(instId=f'{c}-SWAP')
            return position
        except Exception as e:
            print(f'Error [get_position {datetime.now()}]: {e}')
            return 0

    @staticmethod
    def is_any_position_exists():
        try:
            positions = OKX.accountAPI.get_positions()
            position_list = []
            if len(positions['data']) > 0:
                for pos in positions['data']:
                    if float(pos['pos']) != 0:
                        sd = 'Buy' if float(pos['pos']) > 0 else 'Sell'
                        amt = serv.get_position_lots(pos, 'OK')
                        name = convert_name(pos['instId'])
                        inst = [name, sd, amt]
                        position_list.append(inst)
            return position_list
        except Exception as e:
            print(f'Error [is_any_position_exists]: {e}')
            return [1]

    @staticmethod
    def get_last_price(coin):
        try:
            # marketDataAPI =  MarketData.MarketAPI(flag='0')
            c = f'{coin[:-4]}-{coin[-4:]}'
            tk = OKX.publicDataAPI.get_mark_price(instType='MARGIN', instId=c)
            return float(tk['data'][0]['markPx'])
        except Exception as e:
            print(f'Error [get_last_price {datetime.now()}]: {e}')
            return 0

    @staticmethod
    def get_balance() -> float:
        try:
            result = OKX.accountAPI.get_account_balance()
            return result['data'][0]['details'][0]['eq']
        except Exception as e:
            print(f'Error [get_balance {datetime.now()}]: {e}')
            return 0
