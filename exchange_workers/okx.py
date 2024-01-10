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

round_coins = {
    'ADAUSDT': 4,
    'FTMUSDT': 4,
    'HBARUSDT': 5,
    'ARBUSDT': 4,
    'AAVEUSDT': 2,
    'EOSUSDT': 4,
    'EGLDUSDT': 2,
    'FLOWUSDT': 3,
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
    'ADAUSDT': 4,
    'FLOWUSDT': 3,
    'AXSUSDT': 3,
    'SOLUSDT': 2,
    'INJUSDT': 3,
    'GRTUSDT': 4,
    'DOGEUSDT': 5,
    'SNXUSDT': 3,
    'APTUSDT': 4,
    'NEOUSDT': 3,
    'SUIUSDT': 4,
    'RNDRUSDT': 3,
    'XMRUSDT': 2,
    'TRXUSDT': 5,
    'UNIUSDT': 3,
    'LTCUSDT': 2,
    'XLMUSDT': 4,
    'AVAXUSDT': 3,
    'STXUSDT': 4,
    'SANDUSDT': 4,
    'THETAUSDT': 3,
    'APEUSDT': 3,
    'DYDXUSDT': 3,
    'IOTAUSDT': 4,
    'LINKUSDT': 3,
    'OPUSDT': 4,
    'QNTUSDT': 2,
}

amount_lot = {
    'MATICUSDT': 10,
    'XRPUSDT': 100,#1
    'DOGEUSDT': 1000,#2
    'KAVAUSDT': 50,#3
    'IOTAUSDT': 10,#4
    'SANDUSDT': 10,#1
    'EOSUSDT': 10,#2
    'ATOMUSDT': 40,#3
    'LINKUSDT': 1,#4
    'ADAUSDT': 100,#1
    'GRTUSDT': 10,#2
    'AAVEUSDT': 0.1,#3
    'FILUSDT': 0.1,#4
    'ALGOUSDT': 10,#1
    'EGLDUSDT': 0.1,#2
    'AVAXUSDT': 1,#3
    'XMRUSDT': 30,#4
    'AXSUSDT': 0.1,#1
    'NEOUSDT': 1,#2
    'THETAUSDT': 10,#3
    'GALAUSDT': 10,#4
    'MANAUSDT': 10,#1
    'FTMUSDT': 10,#2
    'SOLUSDT': 1,#3
    'DYDXUSDT': 1,#4
    'UNIUSDT': 1,#1
    'MINAUSDT': 1,#2
    'HBARUSDT': 100,#3
    'STXUSDT': 10,#4
    'APTUSDT': 1,#1
    'ARBUSDT': 10,#2
    'APEUSDT': 0.1,#3
    'OPUSDT': 1,#4
    'INJUSDT': 0.1,#1
    'QNTUSDT': 2,#2
}

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
            print(f'Error: [is_contract_exist] {e}')

    @staticmethod
    def open_order(ordType: str, coin: str, sd: str, amount_usdt: int, reduceOnly: bool):
        try:
            side = 'buy' if sd == 'Buy' else 'sell'
            c = f'{coin[:-4]}-{coin[-4:]}'
            last_price = OKX.get_last_price(coin)
            pr = 0
            if side == 'buy':
                pr = last_price * (1+0.0001)
            else:
                pr = last_price * (1-0.0001)
            lot = (amount_usdt / last_price) // amount_lot[coin]
            if reduceOnly == True:
                side = 'sell' if sd == 'Buy' else 'buy'
                lot = lot*2
            if lot < 1:
                lot = 1
            res = OKX.futuresAPI.place_order(instId=f'{c}-SWAP', tdMode='cross', side=side, ordType=ordType, sz=lot, px=pr, ccy='USDT', reduceOnly=reduceOnly) #isolated

            order_id = res['data'][0]['ordId']
            return order_id, pr
        except Exception as e:
            print(f'Error [open_order]: {e}')
            return 0, 0
        
    
    @staticmethod
    def open_order_with_sl(ordType: str, coin: str, sd: str, amount_usdt: int, SL_perc: float, TP_perc: float = 0) -> str:
        try:
            side = 'buy' if sd == 'Buy' else 'sell'
            c = f'{coin[:-4]}-{coin[-4:]}'
            last_price = OKX.get_last_price(coin)
            pr = 0
            if side == 'buy':
                pr = last_price * (1+0.0001)
            else:
                pr = last_price * (1-0.0001)
            lot = (amount_usdt / last_price) // amount_lot[coin]
            
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
            res = OKX.futuresAPI.place_order(instId=f'{c}-SWAP', tdMode='cross', side=side, ordType=ordType, sz=lot, px=pr, ccy='USDT', slTriggerPx=price_sl, slOrdPx=slOrdPx) #isolated

            order_id = res['data'][0]['ordId']
            return order_id, pr
        except Exception as e:
            print(f'Error [open_order_with_sl]: {e}')
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
            print(f'Error [cancel_all_orders]: {e}')
    
    @staticmethod
    def cancel_algo_order(coin: str, ordId: str) -> str:
        c = f'{coin[:-4]}-{coin[-4:]}'
        try:
            algo_orders = [
                {"instId": f'{c}-SWAP', "algoId": ordId},
            ]
            result = OKX.futuresAPI.cancel_algo_order(algo_orders)
        except Exception as e:
            print(f'Error [cancel_algo_order]: {e}')
    
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
            print(f'Error [cancel_all_algo_orders]: {e}')

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
            amount_lot = amount_lot
            res = OKX.futuresAPI.place_algo_order(
                instId=f'{c}-SWAP',
                tdMode="cross",
                side=side,
                ordType="conditional",
                sz=amount_lot,
                slTriggerPx=price,
                slOrdPx=price * (1 - 0.001) if side == 'sell' else price * (1 + 0.001)
            )
            order_id = 0
            if 'data' in res:
                if len(res['data']) > 0:
                    order_id = res['data'][0]['algoId']
            return order_id
        except Exception as e:
            print(f'Error [open_SL]: {e}')
            return 0
    
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
            print(f'Error [open_TP]: {e}')
            return 0
    
    @staticmethod
    def get_position(coin: str):
        try:
            c = f'{coin[:-4]}-{coin[-4:]}'
            position = OKX.accountAPI.get_positions(instId=f'{c}-SWAP')
            return position
        except Exception as e:
            print(f'Error [get_position]: {e}')
            return 0

    @staticmethod
    def get_last_price(coin):
        try:
            # marketDataAPI =  MarketData.MarketAPI(flag='0')
            c = f'{coin[:-4]}-{coin[-4:]}'
            tk = OKX.publicDataAPI.get_mark_price(instType='MARGIN', instId=c)
            return float(tk['data'][0]['markPx'])
        except Exception as e:
            print(f'Error [get_last_price]: {e}')
            return 0

    @staticmethod
    def get_balance() -> float:
        try:
            result = OKX.accountAPI.get_account_balance()
            return result['data'][0]['details'][0]['eq']
        except Exception as e:
            print(f'Error [get_balance]: {e}')
            return 0
