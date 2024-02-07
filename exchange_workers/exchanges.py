from models.settings import Settings
from exchange_workers.kucoin import KuCoin
from exchange_workers.okx import OKX
# from exchange_workers.bitrue import BT
from exchange_workers.bitget import BG
from exchange_workers.bingx import BX
from exchange_workers.bybit import BB
from exchange_workers.bitmart import BM
from exchange_workers.binance import BN
from exchange_workers.gate import GT
from models.position import Position
from helpers.redisdb import RD
from datetime import datetime
import helpers.telegr as tel
import traceback
import shared_vars as sv
import json
import time

def place_limit_order(settings: Settings, sd: str):
    try:
        ord_id, pr = 0,0
        if sv.settings_gl.exchange =='BB':
            ord_id, pr = BB.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'KC':
            # ord_id, pr = KuCoin.open_limit_order(settings.coin, sd, settings.amount_usdt)
            ord_id, pr = KuCoin.open_market_order(settings.coin, sd, settings.amount_usdt)
        elif sv.settings_gl.exchange == 'OK':
            ord_id, pr = OKX.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'BG':
            ord_id, pr = BG.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'BX':
            ord_id, pr = BX.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'BM':
            ord_id, pr = BM.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'GT':
            ord_id, pr = GT.open_order(settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'BN':
            ord_id, pr = BN.open_order('market', settings.coin, sd, settings.amount_usdt, False)
    except Exception as e:
        print(f'Error [place_market_order {datetime.now()}] {e}')
        print(traceback.format_exc())
    
    return ord_id, pr
def is_contract_exist(coin: str):
    try:
        res = False
        contracts = []
        with sv.global_var_lock:
            if sv.settings_gl.exchange =='BB':
                res, contracts = BB.is_contract_exist(coin)
            elif sv.settings_gl.exchange == 'KC':
                res, contracts = KuCoin.is_contract_exist(coin)
            elif sv.settings_gl.exchange == 'OK':
                res, contracts = OKX.is_contract_exist(coin)
            elif sv.settings_gl.exchange == 'BG':
                res, contracts = BG.is_contract_exist(coin)
            elif sv.settings_gl.exchange == 'BX':
                res, contracts = BX.is_contract_exist(coin)
            elif sv.settings_gl.exchange == 'BM':
                res, contracts = BM.is_contract_exist(coin)
            elif sv.settings_gl.exchange == 'GT':
                res, contracts = GT.is_contract_exist(coin)
            elif sv.settings_gl.exchange == 'BN':
                res, contracts = BN.is_contract_exist(coin)
        return res, contracts
    except Exception as e:
        print(f'Error [place_market_order {datetime.now()}] {e}')
        print(traceback.format_exc())


def place_market_order(settings: Settings, sd: str):
    try:
        if sv.settings_gl.exchange =='BB':
            ord_id, pr = BB.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'KC':
            ord_id, pr = KuCoin.open_market_order(settings.coin, sd, settings.amount_usdt)
        elif sv.settings_gl.exchange == 'OK':
            ord_id, pr = OKX.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'BG':
            ord_id, pr = BG.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'BX':
            ord_id, pr = BX.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'BM':
            ord_id, pr = BM.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'GT':
            ord_id, pr = GT.open_order(settings.coin, sd, settings.amount_usdt, False)
        elif sv.settings_gl.exchange == 'BN':
            ord_id, pr = BN.open_order('market', settings.coin, sd, settings.amount_usdt, False)
        return ord_id, pr
    except Exception as e:
        print(f'Error [place_market_order {datetime.now()}] {e}')
        print(traceback.format_exc())

def cancel_order(settings: Settings, order_id, algo=True):
    try:
        if sv.settings_gl.exchange == 'BB':
            BB.cancel_orders(settings.coin)
        elif sv.settings_gl.exchange == 'KC':
            KuCoin.cancel_order_byId(order_id)
        elif sv.settings_gl.exchange == 'OK':
            if algo == True:
                OKX.cancel_algo_order(settings.coin, order_id)
            else:
                OKX.cancel_order(settings.coin, order_id)
        elif sv.settings_gl.exchange == 'BG':
            if algo == True:
                BG.cancel_tpsl_order(settings.coin, order_id)
            else:
                BG.cancel_normal_order(settings.coin, order_id)
        elif sv.settings_gl.exchange == 'BX':
            BX.cancel_all_orders(settings.coin)
        elif sv.settings_gl.exchange == 'BM':
            BM.cancel_all_orders(settings.coin)
        elif sv.settings_gl.exchange == 'GT':
            GT.cancel_all_orders(settings.coin)
        elif sv.settings_gl.exchange == 'BN':
            BN.cancel_all_orders(settings.coin)
    except Exception as e:
        print(f'Error [cancel_order {datetime.now()}] {e}')
        print(traceback.format_exc())

def cancel_all_orders(coin: str, algo=True, order_id=None):
    try:
        if sv.settings_gl.exchange == 'KC':
            KuCoin.cancel_all_orders(coin)
        elif sv.settings_gl.exchange == 'OK':
            if algo == True:
                OKX.cancel_all_algo_orders(coin)
            else:
                OKX.cancel_all_orders(coin)
        elif sv.settings_gl.exchange == 'BG':
            BG.cancel_all_orders(coin)
        elif sv.settings_gl.exchange == 'BX':
            BX.cancel_all_orders(coin)
        elif sv.settings_gl.exchange == 'BM':
            BM.cancel_trigger_order(coin, order_id)
        elif sv.settings_gl.exchange == 'GT':
            GT.cancel_trigger_all_orders(order_id)
        elif sv.settings_gl.exchange == 'BB':
            BB.cancel_orders(coin)
        elif sv.settings_gl.exchange == 'BN':
            BN.cancel_all_orders(coin)
    except Exception as e:
        print(f'Error [cancel_all_orders {datetime.now()}] {e}')
        print(traceback.format_exc())    
    

def close_limit_time_finish(settings: Settings, position: Position, curent_price: float):
    try:
        sd = 'Buy' if position.signal == 1 else 'Sell'
        order_id = ''
        if sv.settings_gl.exchange == 'KC':
            order_id = KuCoin.open_SL(settings.coin, sd, position.amount, curent_price, 0.0001)
        elif sv.settings_gl.exchange == 'OK':
            order_id = OKX.open_SL(settings.coin, sd, position.amount, curent_price, 0.0001)
        elif sv.settings_gl.exchange == 'BG':
            order_id = BG.open_SL('limit', settings.coin, sd, position.amount, curent_price, 0.0001)
        elif sv.settings_gl.exchange == 'BX':
            order_id = BX.open_SL('limit', settings.coin, sd, position.amount, curent_price, 0.0001)
        elif sv.settings_gl.exchange == 'BM':
            order_id = BM.open_SL('limit', settings.coin, sd, position.amount, curent_price, 0.0001)
        elif sv.settings_gl.exchange == 'BB':
            order_id = BB.open_SL('limit', settings.coin, sd, position.amount, curent_price, 0.0001)
        elif sv.settings_gl.exchange == 'GT':
            order_id, _ = GT.open_order(settings.coin, sd, settings.amount_usdt, True)
        elif sv.settings_gl.exchange == 'BN':
            order_id = BN.open_SL('limit', settings.coin, sd, position.amount, curent_price, 0.0001)
        return order_id
    except Exception as e:
        print(f'Error [close_limit_time_finish {datetime.now()}] {e}')
        print(traceback.format_exc())

def add_Stop_Loss(settings: Settings, position: Position, open_price: float):
    try:
        sd = 'Buy' if position.signal == 1 else 'Sell'
        order_id = ''
        if sv.settings_gl.exchange == 'KC':
            order_id = KuCoin.open_SL(settings.coin, sd, position.amount, open_price, settings.stop_loss)
        elif sv.settings_gl.exchange == 'OK':
            order_id = OKX.open_SL(settings.coin, sd, position.amount, open_price, settings.stop_loss)
        elif sv.settings_gl.exchange == 'BG':
            order_id = BG.open_SL('market', settings.coin, sd, position.amount, open_price, settings.stop_loss)
        elif sv.settings_gl.exchange == 'BX':
            order_id = BX.open_SL('market', settings.coin, sd, position.amount, open_price, settings.stop_loss)
        elif sv.settings_gl.exchange == 'BM':
            order_id = BM.open_SL('market', settings.coin, sd, position.amount, open_price, settings.stop_loss)
        elif sv.settings_gl.exchange == 'GT':
            order_id = GT.open_SL(settings.coin, sd, position.amount, open_price, settings.stop_loss)
        elif sv.settings_gl.exchange == 'BB':
            order_id = BB.open_SL('market', settings.coin, sd, position.amount, open_price, settings.stop_loss)
        elif sv.settings_gl.exchange == 'BN':
            order_id = BN.open_SL('market', settings.coin, sd, position.amount, open_price, settings.stop_loss)
        return order_id
    except Exception as e:
        print(f'Error [add_Stop_Loss {datetime.now()}] {e}')
        print(traceback.format_exc())

def close_time_finish(settings: Settings, position: Position):
    try:
        sd = 'Buy' if position.signal == 1 else 'Sell'
        if sv.settings_gl.exchange =='BB':
            BB.open_order('market', position.coin, sd, settings.amount_usdt, True)
        elif sv.settings_gl.exchange == 'KC':
            KuCoin.close_position_market(position.coin, sd)
        elif sv.settings_gl.exchange == 'OK':
            OKX.open_order('market', position.coin, sd, settings.amount_usdt, True)
        elif sv.settings_gl.exchange == 'BG':
            BG.open_order('market', position.coin, sd, settings.amount_usdt, True, position.amount)
        elif sv.settings_gl.exchange == 'BX':
            BX.open_order('market', position.coin, sd, settings.amount_usdt, True, position.amount)
        elif sv.settings_gl.exchange == 'BM':
            BM.open_order('market', position.coin, sd, settings.amount_usdt, True, position.amount)
        elif sv.settings_gl.exchange == 'BN':
            BN.open_order('market', position.coin, sd, settings.amount_usdt, True, position.amount)
        elif sv.settings_gl.exchange == 'GT':
            GT.open_order(position.coin, sd, settings.amount_usdt, True)
    except Exception as e:
        print(f'Error [close_time_finish {datetime.now()}] {e}')
        print(traceback.format_exc())

def get_last_price(coin: str):
    try:
        if sv.settings_gl.exchange == 'BB':
            return BB.get_last_price(coin)
        elif sv.settings_gl.exchange == 'KC':
            return KuCoin.get_last_price(coin)
        elif sv.settings_gl.exchange == 'OK':
            return OKX.get_last_price(coin)
        elif sv.settings_gl.exchange == 'BG':
            return BG.get_last_price(coin)
        elif sv.settings_gl.exchange == 'BX':
            return BX.get_last_price(coin)
        elif sv.settings_gl.exchange == 'BM':
            return BM.get_last_price(coin)
        elif sv.settings_gl.exchange == 'GT':
            return GT.get_last_price(coin)
        elif sv.settings_gl.exchange == 'BN':
            return BN.get_last_price(coin)
    except Exception as e:
        print(f'Error [get_balance {datetime.now()}] {e}')
        print(traceback.format_exc())

def get_balance():
    try:
        balance = 0
        if sv.settings_gl.exchange == 'BB':
            balance = BB.get_balance('USDT')
        elif sv.settings_gl.exchange == 'KC':
            balance = KuCoin.get_balance('USDT')
        elif sv.settings_gl.exchange == 'OK':
            balance = OKX.get_balance()
        elif sv.settings_gl.exchange == 'BG':
            balance = BG.get_balance()
        elif sv.settings_gl.exchange == 'BX':
            balance = BX.get_balance()
        elif sv.settings_gl.exchange == 'BM':
            balance = BM.get_balance()
        elif sv.settings_gl.exchange == 'GT':
            balance = GT.get_balance()
        elif sv.settings_gl.exchange == 'BN':
            balance = BN.get_balance()
        return float(balance)
    except Exception as e:
        print(f'Error [get_balance {datetime.now()}] {e}')
        print(traceback.format_exc())


def is_position_exist(position):
    try:
        if sv.settings_gl.exchange == 'BB':
            if float(position['size']) == 0:
                return False, position
        elif sv.settings_gl.exchange == 'KC':
            if 'currentQty' in position:
                if float(position['currentQty']) == 0:
                    return False, position
            else:
                return False, position
        elif sv.settings_gl.exchange == 'OK':
            if 'data' in position:
                if len(position['data'])>0:
                    if position['data'][0]['avgPx'] == '':
                        return False, position
                else:
                    return False, position
            else:
                return False, position
        elif sv.settings_gl.exchange == 'BG':
            if position is not None:
                if position['available'] == '0':
                    return False, position
            elif position is None:
                return False, position
        elif sv.settings_gl.exchange == 'BX':
            if position is None:
                return False, position
        elif sv.settings_gl.exchange == 'BM':
            if position is None:
                return False, position
        elif sv.settings_gl.exchange == 'GT':
            if position['size'] == 0:
                return False, position
        elif sv.settings_gl.exchange == 'BN':
            if float(position['positionAmt']) == 0:
                return False, position
        # elif sv.settings_gl.exchange == 'BT':
        #     if position is None:
        #         return False, position
        return True, position
    except Exception as e:
        print(f'Error [is_position_exist {datetime.now()}] {e}')
        print(traceback.format_exc())

def get_position_entry_price(position):
    try:
        if sv.settings_gl.exchange == 'KC':
            return float(position['avgEntryPrice'])
        elif sv.settings_gl.exchange == 'OK':
            return float(position['data'][0]['avgPx'])
        elif sv.settings_gl.exchange == 'BG':
            if position is not None:
                return float(position['averageOpenPrice'])
        elif sv.settings_gl.exchange == 'BX':
            return float(position['avgPrice'])
        elif sv.settings_gl.exchange == 'BM':
            return float(position['open_avg_price'])
        elif sv.settings_gl.exchange == 'GT':
            return float(position['entry_price'])
        elif sv.settings_gl.exchange == 'BB':
            return float(position['avgPrice'])
        elif sv.settings_gl.exchange == 'BN':
            return float(position['entryPrice'])
        # elif sv.settings_gl.exchange == 'BT':
        #     if position is not None:
        #         return float(position['openPrice'])
        else: return 0
    except Exception as e:
        print(f'Error [get_position_entry_price {datetime.now()}] {e}')
        print(traceback.format_exc())
    
def get_position_lots(position):
    try:
        if sv.settings_gl.exchange == 'KC':
            return int(position['currentQty'])
        elif sv.settings_gl.exchange == 'OK':
            return int(position['data'][0]['pos'])
        elif sv.settings_gl.exchange == 'BG':
            return float(position['available'])
        elif sv.settings_gl.exchange == 'BX':
            return float(position['positionAmt'])
        elif sv.settings_gl.exchange == 'BM':
            return float(position['current_amount'])
        elif sv.settings_gl.exchange == 'GT':
            return float(position['size'])
        elif sv.settings_gl.exchange == 'BB':
            return float(position['size'])
        elif sv.settings_gl.exchange == 'BN':
            print(position)
            return float(position['positionAmt'])
        # elif sv.settings_gl.exchange == 'BT':
        #     return float(position['volume'])
    except Exception as e:
        print(f'Error [get_position_lots {datetime.now()}] {e}')
        print(traceback.format_exc())

def get_position_info(coin: str, signal: int):
    try:
        position = None
        if sv.settings_gl.exchange == 'BB':
            position = BB.get_position(coin)
        elif sv.settings_gl.exchange == 'KC':
            position = KuCoin.get_position(coin)
        elif sv.settings_gl.exchange == 'OK':
            position = OKX.get_position(coin)
        elif sv.settings_gl.exchange == 'BG':
            position = BG.get_position(coin, signal)
        elif sv.settings_gl.exchange == 'BX':
            position = BX.get_position(coin)
        elif sv.settings_gl.exchange == 'BM':
            position = BM.get_position(coin)
        elif sv.settings_gl.exchange == 'GT':
            position = GT.get_position(coin)
        elif sv.settings_gl.exchange == 'BN':
            position = BN.get_position(coin)
        # elif sv.settings_gl.exchange == 'BT':
        #     position = BT.get_position(coin, signal)
        return position
    except Exception as e:
        print(f'Error [get_position_info {datetime.now()}] {e}')
        print(traceback.format_exc())

def get_unrealized_PNL(responce: dict):
    try:
        if sv.settings_gl.exchange == 'BB':
            return float(responce['unrealisedPnl'])
        elif sv.settings_gl.exchange == 'KC':
            return float(responce['unrealisedPnl'])
        elif sv.settings_gl.exchange == 'OK':
            return float(responce['data'][0]['uplLastPx'])
        elif sv.settings_gl.exchange == 'BG':
            return float(responce['unrealizedPL'])
        elif sv.settings_gl.exchange == 'BX':
            return float(responce['unrealizedProfit'])
        elif sv.settings_gl.exchange == 'BM':
            return float(responce['unrealized_value'])
        elif sv.settings_gl.exchange == 'GT':
            return float(responce['unrealised_pnl'])
        elif sv.settings_gl.exchange == 'BN':
            return float(responce['unrealizedProfit'])
        # elif sv.settings_gl.exchange == 'BT':
        #     return float(responce['openRealizedAmount'])
    except Exception as e:
        print(f'Error [get_unrealized_PNL {datetime.now()}] {e}')
        print(traceback.format_exc())

async def take_position(settings: Settings, buy_sell: int):
    try:
        bs = 'Buy' if buy_sell == 1 else 'Sell'
        order_id = ''
        timest = datetime.now().timestamp()
        print(settings.coin, bs, settings.amount_usdt)

        order_id, prise_open = place_market_order(settings, bs)
        print(f'Position trying to plase. Order_id = {order_id}')
        open_time = datetime.now().strftime(sv.time_format)
        time.sleep(2)
        is_pos_exist, position = is_position_exist(get_position_info(settings.coin, buy_sell))
        if is_pos_exist == True:
            old_balance = get_balance()
            entry_pr = get_position_entry_price(position)
            lots = get_position_lots(position)
            current_position = Position(settings.coin, open_time , entry_pr, old_balance, lots, buy_sell, 'Market', settings.timeframe, settings.tos)
            RD.rewrite_one_field(f'exs_pos:{settings.name}', settings.coin, json.dumps(vars(current_position)))
            await tel.send_inform_message(settings.telegram_token, f'Position was taken successfully: {str(current_position)}', '', False)
            current_position.order_sl_id = add_Stop_Loss(settings, current_position, entry_pr)
            return True, current_position
        else:
            await tel.send_inform_message(settings.telegram_token, 'Position doesn\'t exist after order', '', False)
            return False, None
    except Exception as e:
        print(f'Error [place_universal_order {datetime.now()}] {e}')
        print(traceback.format_exc())


async def place_universal_order(settings: Settings, buy_sell: int):
    try:
        bs = 'Buy' if buy_sell == 1 else 'Sell'
        order_id = ''
        timest = datetime.now().timestamp()
        print(settings.coin, bs, settings.amount_usdt)

        order_id, prise_want_open = place_limit_order(settings, bs)
        open_time = datetime.now().strftime(sv.time_format)
        print('order placed')
        while True:
            is_pos_exist, position = is_position_exist(get_position_info(settings.coin, buy_sell))
            if is_pos_exist == True:
                old_balance = get_balance()
                entry_pr = get_position_entry_price(position)
                lots = get_position_lots(position)
                current_position = Position(settings.coin, open_time , entry_pr, old_balance, lots, buy_sell, 'Limit', settings.timeframe)
                # fb.write_settings('existing_positions', settings.name, f'{settings.coin}', current_position)
                RD.rewrite_one_field(f'exs_pos:{settings.name}', settings.coin, json.dumps(vars(current_position)))
                await tel.send_inform_message(settings.telegram_token, f'Position was taken successfully: {str(current_position)}', '', False)
                current_position.order_sl_id = add_Stop_Loss(settings, current_position, entry_pr)
                return True, current_position
            
            time.sleep(1)

            time_obj = datetime.strptime(open_time, sv.time_format)
            duration = datetime.now() - time_obj
            duration_seconds = duration.total_seconds()

            if timest + settings.message_timer < datetime.now().timestamp():
                print(f'trying to take position {duration}')
                await tel.send_inform_message(settings.telegram_token, f'Trying to take position {settings.coin} {duration}', '', False)
                timest = datetime.now().timestamp()
            
            if duration_seconds > 6:
                break

        cancel_order(settings, order_id, False)
        curr_price = get_last_price(settings.coin)

        order_to_take = False
        if curr_price < prise_want_open* (1+0.002) and bs == 'Buy':
            order_to_take = True
        elif curr_price > prise_want_open* (1-0.002) and bs == 'Sell':
            order_to_take = True
        
        if order_to_take:
            place_market_order(settings, bs)
            is_pos_exist, position = is_position_exist(get_position_info(settings.coin, buy_sell))
            if is_pos_exist:
                old_balance = get_balance()
                entry_pr = get_position_entry_price(position)
                lots = get_position_lots(position)
                current_position = Position(settings.coin, open_time , entry_pr, old_balance, lots, buy_sell, 'Market', settings.timeframe)
                RD.rewrite_one_field(f'exs_pos:{settings.name}', settings.coin, json.dumps(vars(current_position)))
                await tel.send_inform_message(settings.telegram_token, f'Position was taken successfully: {str(current_position)}', '', False)
                current_position.order_sl_id = add_Stop_Loss(settings, current_position, entry_pr)
                return True, current_position
                        
        await tel.send_inform_message(settings.telegram_token, 'Position doesn\'t exist after order', '', False)
        return False, None
    except Exception as e:
        print(f'Error [place_universal_order {datetime.now()}] {e}')
        print(traceback.format_exc())

        