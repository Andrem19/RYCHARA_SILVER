import json
from datetime import datetime
import shared_vars as sv
from exchange_workers.kucoin import KuCoin
import exchange_workers.exchanges as ex
from helpers.redisdb import RD
import work
import time
from models.settings import Settings
import threading
import helpers.services as serv
import asyncio
import uuid
import copy

def handler(sign_dic: dict):
    position_lenth = 0
    exchanges_positions_limit = None
    with sv.global_var_lock:
        exchanges_positions_limit = RD.read_dict(f'individual_settings:{sv.settings_gl.name}')
        position_lenth = len(sv.coins_in_work)
        if position_lenth >= int(sign_dic['numbers']):
            return
    timestamp = float(sign_dic['timestamp'])
    is_position_exist, position = ex.is_position_exist(ex.get_position_info(sign_dic['name'], int(sign_dic['signal'])))
    if (timestamp+40 > datetime.now().timestamp() and is_position_exist == False and sign_dic['name'] not in sv.coins_in_work) or (timestamp == 111 and is_position_exist == False and sign_dic['name'] not in sv.coins_in_work):
        sl = float(sign_dic['sl'])
        uid =  uuid.uuid4()
        target_len = int(sign_dic['targ_len'])
        timeframe = int(sign_dic['timeframe'])
        coin_symbol = sign_dic['name']
        signal = int(sign_dic['signal'])
        koff = float(sign_dic['koff'])
        type_of_signal = sign_dic['type_of_signal']

        settings = Settings()
        set_dict = RD.read_dict('settings:worker')
        sv.settings_gl.from_dict(set_dict)
        amount_max = sv.settings_gl.max_amount

        with sv.global_var_lock:
            settings = copy.deepcopy(sv.settings_gl)
            sv.coins_in_work[coin_symbol] = sign_dic
        
        settings.pause = int(exchanges_positions_limit['pause'])
        settings.amount_usdt = float(exchanges_positions_limit['amount']) * koff

        settings.coin = coin_symbol
        settings.my_uid = str(uid)
        settings.target_len = target_len 
        settings.timeframe = timeframe
        settings.stop_loss = sl
        settings.tos = type_of_signal

        if settings.amount_usdt > amount_max:
            settings.amount_usdt = amount_max

        settings.take_profit = 0.2
        close_thread = threading.Thread(target=asyncio.run, args=(work.open_position(settings, signal),))
        close_thread.start()
    else:
        print('[handler] didnt pass!')

def decision_maker(signals: list):
    tm_now = time.time()
    if any(tm_now - float(d['timestamp']) <= 40 or float(d['timestamp']) == 111 for d in signals):
        res, coin_exchange_list = ex.is_contract_exist('BTCUSDT')
        signal_collection = collect_signals(signals, coin_exchange_list, tm_now)
        if signal_collection:
            return signal_collection
    return -1

def collect_signals(signals, coin_exchange_list, tm_now):
    collection = []
    for value in signals:
        timestamp = float(value['timestamp'])
        if value['name'] not in coin_exchange_list:
            if int(value['signal']) != 3 and (timestamp+40 > tm_now or timestamp == 111):
                sv.messages_queue.append(f'{sv.settings_gl.name} coin {value["name"]} is not exist on the exchange')
            continue
        if (timestamp+40 > tm_now and int(value['signal']) != 3 and value['name'] not in sv.coins_in_work) or (timestamp == 111 and int(value['signal']) != 3):
            collection.append(value)
    return collection

def get_max_rating_dict(dict_list):
    return copy.deepcopy(max(dict_list, key=lambda x: x['rating']))

def sort_dicts_by_rating(dict_list):
    return sorted(dict_list, key=lambda x: x['rating'], reverse=True)