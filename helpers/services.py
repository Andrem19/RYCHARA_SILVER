import json
import os
import shared_vars as sv
from datetime import datetime
from models.position import Position
from models.settings import Settings
from exchange_workers.kucoin import KuCoin
from exchange_workers.okx import OKX
from exchange_workers.bybit import BB
from exchange_workers.gate import GT
from exchange_workers.binance import BN
from exchange_workers.bitget import BG
from exchange_workers.bitmart import BM
from exchange_workers.bingx import BX
import shutil
import time
from helpers.redisdb import RD
import traceback

def find_common_elements(list1, list2, list3, list4, list5, list6, list7, list8):
    # Преобразуйте списки в множества
    set1 = set(list1)
    set2 = set(list2)
    set3 = set(list3)
    set4 = set(list4)
    set5 = set(list5)
    set6 = set(list6)
    set7 = set(list7)
    set8 = set(list8)

    # Используйте функцию set.intersection() для поиска общих элементов
    common_elements_set = set1.intersection(set2, set3, set4, set5, set6, set7, set8)

    # Преобразуйте множество обратно в список
    common_elements_list = list(common_elements_set)

    return common_elements_list

def get_last_saldo(name: str):
    try:
        result = RD.return_list(f'saldo:{name}', True)
        dict_sal = json.loads(result)
        last_saldo = float(dict_sal['saldo'])
        return round(last_saldo, 4)
    except Exception as e:
        print(e)
        return 0

def write_timestamp(filename):
    with open(filename, 'w') as file:
        file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def read_timestamp(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            timestamp = datetime.strptime(file.read(), '%Y-%m-%d %H:%M:%S')
            return int(timestamp.timestamp())
    else:
        print('file do not exist')




def convert_to_timestamp(date_string):
    if date_string == '0':
        return 0
    try:
        dt = datetime.strptime(date_string, '%d.%m.%y')
        timestamp = dt.timestamp() * 1000
        return int(timestamp)
    except ValueError:
        return -1

def filter_list_by_timestamp(input_list, timestamp):
    if timestamp == 0:
        return input_list
    filtered_list = []
    for item in input_list:
        if item[0] >= timestamp:
            filtered_list.append(item)
    return filtered_list

def convert_seconds_to_period(seconds: float):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = round(seconds % 60, 2)

    period = f"{hours:02}:{minutes:02}:{seconds:02}"
    return period
def remove_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # удалить файл или символическую ссылку
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # удалить директорию и все ее содержимое

def add_coin_take(coin):
    sv.coin_last_take[coin] = datetime.now().timestamp()

def add_coin_close(coin):
    sv.coin_last_close[coin] = datetime.now().timestamp()
def check_coin_last_close(coin):
    with sv.global_var_lock:
        if coin not in sv.coin_last_close:
            return True
        else:
            if datetime.now().timestamp() - 8 > sv.coin_last_take[coin]:
                return True
        return False

def check_coin_last_take(coin):
    with sv.global_var_lock:
        if coin not in sv.coin_last_take:
            return True
        else:
            if datetime.now().timestamp() - 51 > sv.coin_last_take[coin]:
                return True
        return False
            
def change_rating_redis(coin: str, pl_mn: int):
    coin_rating = int(RD.read_dict_field(f'coin:{coin}', 'rating'))
    new_rating = coin_rating + pl_mn if coin_rating != 0 else 0
    RD.rewrite_one_field(f'coin:{coin}', 'rating', new_rating)

def get_position_lots(position, exchange):
    try:
        if exchange == 'KC':
            return int(position['currentQty'])
        elif exchange == 'OK':
            return int(position['data'][0]['pos'])
        elif exchange == 'BG':
            return float(position['available'])
        elif exchange == 'BX':
            return float(position['positionAmt'])
        elif exchange == 'BM':
            return float(position['current_amount'])
        elif exchange == 'GT':
            return float(position.size)
        elif exchange == 'BB':
            return float(position['size'])
        elif exchange == 'BN':
            return float(position['positionAmt'])
        # elif sv.settings_gl.exchange == 'BT':
        #     return float(position['volume'])
    except Exception as e:
        print(f'Error [get_position_lots {datetime.now()}] {e}')
        print(traceback.format_exc())

def close_all_position(coin: str, amt: float, sd: str, exchange: str):
    try:
        if exchange =='BB':
            BB.open_order('market', coin, sd, 2, True)
        elif exchange == 'KC':
            KuCoin.close_position_market(coin, sd)
        elif exchange == 'OK':
            OKX.open_order('market', coin, sd, 2, True)
        elif exchange == 'BG':
            BG.open_order('market', coin, sd, 2, True, amt)
        elif exchange == 'BX':
            BX.open_order('market', coin, sd, 2, True, amt)
        elif exchange == 'BM':
            BM.open_order('market', coin, sd, 2, True, amt)
        elif exchange == 'BN':
            BN.open_order('market', coin, sd, 2, True, amt)
        elif exchange == 'GT':
            GT.open_order(coin, sd, 2, True)
    except Exception as e:
        print(f'Error [close_all_position] {datetime.now()}] {e}')
        print(traceback.format_exc())

def get_exchange_positions():
   bn_pos = BN.is_any_position_exists()
   time.sleep(0.2)
   bb_pos = BB.is_any_position_exists()
   time.sleep(0.2)
   bg_pos = BG.is_any_position_exists()
   time.sleep(0.2)
   bm_pos = BM.is_any_position_exists()
   time.sleep(0.2)
   okx_pos = OKX.is_any_position_exists()
   time.sleep(0.2)
   kc_pos = KuCoin.is_any_position_exists()
   time.sleep(0.2)
   gt_pos = GT.is_any_position_exists()
   time.sleep(0.2)
   bx_pos = BX.is_any_position_exists()

   report = {
       'BN': bn_pos,
       'BB': bb_pos,
       'BG': bg_pos,
       'BM': bm_pos,
       'OK': okx_pos,
       'KC': kc_pos,
       'GT': gt_pos,
       'BX': bx_pos,
   }
   
   return report
