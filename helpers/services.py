import json
import os
import shared_vars as sv
from datetime import datetime
from models.position import Position
from models.settings import Settings
import shutil


def check_exclude_coins(exchange: str, coin: str):
    if exchange =='OK':
        if coin in sv.exclude_okx:
            return False
    elif exchange == 'KC':
        if coin in sv.exclude_kc:
            return False
    elif exchange == 'BG':
        if coin in sv.exclude_bg:
            return False
    elif exchange == 'BX':
        if coin in sv.exclude_bx:
            return False
    elif exchange == 'BM':
        if coin in sv.exclude_bm:
            return False
    elif exchange == 'GT':
        if coin in sv.exclude_gt:
            return False
    elif exchange == 'BB':
        if coin in sv.exclude_bb:
            return False
    elif exchange == 'BN':
        if coin in sv.exclude_bn:
            return False
    return True

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
            