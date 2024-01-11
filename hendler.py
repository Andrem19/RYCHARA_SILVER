import json
from datetime import datetime
import shared_vars as sv
from exchange_workers.bybit_http import BybitAPI
from exchange_workers.kucoin import KuCoin
import helpers.firebase as fb
import exchange_workers.exchanges as ex
from helpers.redisdb import RD
import work
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
        if position_lenth >= int(exchanges_positions_limit['numbers']):
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
        rating = int(sign_dic['rating'])
        type_of_signal = int(sign_dic['type'])

        settings = Settings()
        set_dict = RD.read_dict('settings:worker')
        sv.settings_gl.from_dict(set_dict)
        amount_max = sv.settings_gl.amount_usdt

        with sv.global_var_lock:
            settings = copy.deepcopy(sv.settings_gl)
            sv.coins_in_work[coin_symbol] = sign_dic
        
        settings.pause = int(exchanges_positions_limit['pause'])
        settings.amount_usdt = int(exchanges_positions_limit['amount'])
        settings.coin = coin_symbol
        settings.my_uid = str(uid)
        settings.coin_rating = rating
        settings.target_len = target_len 
        settings.timeframe = timeframe

        if settings.timeframe !=1 and sl < 0.01:
            settings.stop_loss = 0.01
        elif settings.timeframe !=1 and sl > 0.02:
            settings.stop_loss = 0.02

        if settings.timeframe == 1:
            settings.stop_loss = 0.006
        if settings.amount_usdt > amount_max:
            settings.amount_usdt = amount_max

        settings.take_profit = settings.stop_loss * 7
        settings.type_of_signal = type_of_signal
        close_thread = threading.Thread(target=asyncio.run, args=(work.open_position(settings, signal),))
        close_thread.start()
    else:
        print('[handler] didnt pass!')


def decision_maker(signals: list):
    numbers_of_signals = 0
    res, coin_exchange_list = ex.is_contract_exist('BTCUSDT')
    signal_collection = []
    for value in signals:
        if value['name'] not in coin_exchange_list:
            continue
        tm = value['timestamp']
        timestamp = float(tm)
        if timestamp+40 > datetime.now().timestamp() and value['signal'] !=3:
            numbers_of_signals+=1
            if numbers_of_signals > 3:
                with sv.global_var_lock:
                    sv.high_vol = True
        if (timestamp+40 > datetime.now().timestamp() and value['signal'] != 3 and value['name'] not in sv.coins_in_work) or (timestamp == 111 and value['signal'] != 3):
            signal_collection.append(value)
        else:
            continue
    if len(signal_collection) > 0:
        max_rating_dict = sort_dicts_by_rating(signal_collection)
        if len(signal_collection) > 3:
            with sv.global_var_lock:
                sv.high_vol = True
        # print(f'------------------------{datetime.now()}------------------------')
        # print(f'Decisionmaker return signal: {max_rating_dict["signal"]} coin: {max_rating_dict["name"]} tf: {max_rating_dict["timeframe"]}')
        # print(f'--------------------------------------------------------------------------')
        return max_rating_dict
    return -1


def get_max_rating_dict(dict_list):
    return copy.deepcopy(max(dict_list, key=lambda x: x['rating']))

def sort_dicts_by_rating(dict_list):
    return sorted(dict_list, key=lambda x: x['rating'], reverse=True)