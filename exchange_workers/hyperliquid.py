import threading
from models.settings import Settings
from hyperliquid.info import Info
from hyperliquid.utils import constants
from decouple import config
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange
import eth_account
from eth_account.signers.local import LocalAccount

def setup(address, api, api_secret):
    account: LocalAccount = eth_account.Account.from_key(api_secret)
    if address == "":
        address = account.address
    print("Running with account address:", address)
    if address != account.address:
        print("Running with agent address:", account.address)
    info = Info(constants.MAINNET_API_URL, True)
    exchange = Exchange(account, constants.MAINNET_API_URL, account_address=address)
    return address, info, exchange

class HL:

    init_lock = threading.Lock()

    info: Info = None
    exchange = None
    
    address = None
    api_key = None
    secret_key = None

    @staticmethod
    def init(settings: Settings):
        # Check if the variables are already set
        if HL.info is not None:
                return
        # Acquire the lock to ensure only one thread initializes the variables
        with HL.init_lock:
            
            HL.api_key = config(f'{settings.API_KEY}X')
            HL.secret_key = config(settings.SECRET_KEY)
            HL.address, HL.info, HL.exchange = setup(config(settings.API_KEY), HL.api_key, HL.secret_key)
    
    @staticmethod
    def get_balance():
        try:
            result = HL.info.user_state(HL.address)
            return float(result['crossMarginSummary']['accountValue'])
        except Exception as e:
            print(f'Error: {e}')
            return 0
    
    @staticmethod
    def get_position(coin: str) -> dict | None:
        try:
            c = coin[:-4]
            result = HL.info.user_state(HL.address)
            if 'assetPositions' in result:
                if len(result['assetPositions'])>0:
                    for pos in result['assetPositions']:
                        if pos['position']['coin'] == c:
                            return {
                                'positionValue': pos['position']['positionValue'],
                                'unrealizedPnl': pos['position']['unrealizedPnl'],
                                'size': abs(float(pos['position']['szi'])),
                                'entryPx': pos['position']['entryPx'],
                            }
            return None
        except Exception as e:
            print(f'Error: {e}')
            return 0

    @staticmethod
    def is_contract_exist(coin:str):
        try:
            symbols = []
            contracts = HL.info.meta()
            for cont in contracts['universe']:
                s = f'{cont["name"]}USDT'
                symbols.append(s)
            if coin in symbols:
                return True, symbols
            return False, symbols
        except Exception as e:
            print(f'Error: [is_contract_exist] {e}')

    @staticmethod
    def instrument_info(symbol: str) -> dict:
        try:
            s = symbol[:-4]
            contracts = HL.info.meta()
            for cont in contracts['universe']:
                if cont['name']==s:
                    return cont #{'maxLeverage': 50, 'name': 'BTC', 'onlyIsolated': False, 'szDecimals': 5}
        except Exception as e:
            print(f"Error [instrument_info]: {e}")
            return None
        
    @staticmethod
    def set_leverage(symbol: str, leverage: int, onlyIsolated: bool):
        try:
            s = symbol[:-4]
            HL.exchange.update_leverage(leverage, s, not onlyIsolated)
        except Exception as e:
            print(f'[set_leverage] {e}')

    @staticmethod
    def is_any_position_exists():
        try:
            position_list = []
            result = HL.info.user_state(HL.address)
            if 'assetPositions' in result:
                if len(result['assetPositions'])>0:
                    for position in result['assetPositions']:
                        sd = 'Buy' if float(position['position']['szi']) > 0 else 'Sell'
                        amt = abs(float(position['position']['szi']))
                        name = f"{position['position']['coin']}USDT"
                        inst = [name, sd, amt]
                        position_list.append(inst)

            return position_list
        except Exception as e:
            print(f'Error [is_any_position_exists]: {e}')
            return 0
        
    @staticmethod
    def get_last_price(coin):
        try:
            s = coin[:-4]
            res = HL.info.all_mids()
            curent_price = float(res[s])
            return curent_price
        except Exception as e:
            print(f'Error [get_last_price]: {e}')
            return 0

    @staticmethod
    def cancel_all_orders(coin: str) -> str:
        try:
            c = coin[:-4]
            open_orders = HL.info.open_orders(HL.address)
            print(open_orders)
            for open_order in open_orders:
                if open_order["coin"] == c:
                    print(f"cancelling order {open_order}")
                    HL.exchange.cancel(open_order["coin"], open_order["oid"])
        except Exception as e:
            print(f'Error [cancel_all_orders]: {e}')
        
    @staticmethod
    def open_market_order(coin: str, sd: str, amount_usdt: int, reduceOnly: bool, amount_coins = 0.0):
        try:
            c = coin[:-4]
            last_price = HL.get_last_price(coin)
            inst_info = HL.instrument_info(coin)#{'maxLeverage': 50, 'name': 'BTC', 'onlyIsolated': False, 'szDecimals': 5}
            szDecimals = int(inst_info['szDecimals'])
            size = round(amount_usdt / last_price, szDecimals)
            leverage = 20
            max_lever = int(inst_info['maxLeverage'])
            if max_lever<20:
                leverage = max_lever
            onlyIsolated = inst_info['onlyIsolated']
            HL.set_leverage(coin, leverage, onlyIsolated)
            
            side = True if sd == 'Buy' else False

            order = None
            if reduceOnly:
                order = HL.exchange.market_close(c, amount_coins, None, 0.01)
            else:
                order = HL.exchange.market_open(c, side, size, None, 0.01)
                
            if order['status'] == 'ok':
                for ord in order['response']['data']['statuses']:
                    if 'filled' in ord:
                        return ord['filled']['oid'], ord['filled']['avgPx']
            else:
                return 0, last_price
        except Exception as e:
            print(f'Error [open_market_order]: {e}')
            return 0,0
        
    @staticmethod
    def open_SL(coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
        try:
            c = coin[:-4]
            # inst_info = HL.instrument_info(coin)#{'maxLeverage': 50, 'name': 'BTC', 'onlyIsolated': False, 'szDecimals': 5}
            # szDecimals = int(inst_info['szDecimals'])
            position_side = False if sd == 'Buy' else True

            price = 0
            if sd == 'Buy':
                price = open_price * (1-SL_perc)
            elif sd == 'Sell':
                price = open_price * (1+SL_perc)

            trigger_px = price * (1 - 0.001) if sd == 'Sell' else price * (1 + 0.001)
            triggerPx = round(float(f"{trigger_px:.5g}"), 6)
            px = round(float(f"{price:.5g}"), 6)
            stop_order_type = {"trigger": {"triggerPx": triggerPx, "isMarket": True, "tpsl": "sl"}}
            stop_result = HL.exchange.order(c, position_side, amount_lot, px, stop_order_type, reduce_only=True)
            print(stop_result)
            # if 'result' in order:
            #     return order['result']
            # else:
            #     return 0
        except Exception as e:
            print(f'Error [open_SL]: {e}')
            return 0