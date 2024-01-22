import shared_vars as sv
import helpers.services as serv
from models.settings import Settings
from exchange_workers.kucoin import KuCoin
from exchange_workers.okx import OKX
from exchange_workers.bybit import BB
from exchange_workers.gate import GT
from exchange_workers.binance import BN
from exchange_workers.bitget import BG
from exchange_workers.bitmart import BM
from exchange_workers.bingx import BX
import exchange_workers.binance as b
import requests
import exchange_workers.exchanges as ex
from decouple import config
import json
from datetime import datetime
import time
from helpers.redisdb import RD
# RD.initialize()


# import requests
# import time
# import hmac
# import hashlib

# # Ваши ключи API
# api_key = config('BNAPI_1')
# secret_key = config('BNSECRET_1')

# # Базовый URL для Binance API
# base_url = 'https://api.binance.com'

# # Эндпоинт для проверки статуса аккаунта
# endpoint = '/sapi/v1/account/apiTradingStatus'

# # Получаем текущее время в миллисекундах
# timestamp = int(time.time() * 1000)

# # Формируем строку запроса
# query_string = f'timestamp={timestamp}'

# # Создаем подпись HMAC SHA256
# signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

# # Добавляем подпись к строке запроса
# query_string += f'&signature={signature}'

# # Полный URL запроса
# url = base_url + endpoint + '?' + query_string

# # Заголовки запроса
# headers = {
#     'X-MBX-APIKEY': api_key
# }

# # Отправляем запрос
# response = requests.get(url, headers=headers)

# # Выводим ответ
# print(response.json())

# res = requests.get('https://api.binance.com/sapi/v1/account/status')
# print(res.text)
# serv.change_rating_redis('ADAUSDT', 1)
# RD.write_dict('coin:ADAUSDT', {'rating': 31})
# def event_handler(message):
#     print('Event received:', message)
# def run_listner():
#     RD.initialize()

#     pubsub = RD._client.pubsub()
#     pubsub.psubscribe(**{"__keyspace@0__:trigger": event_handler})
#     thread = pubsub.run_in_thread(sleep_time=0.01)
# # RD.initialize()
# # last_saldo = serv.get_last_saldo('BN_1')
# # print(last_saldo)
# run_listner()
# while True:
#     time.sleep(3)
#     print('loop')

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BM'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BM.init(sv.settings_gl)

# response = requests.get(f'https://api-cloud.bitmart.com/contract/public/details?symbol=SOLUSDT')
# res = response.json()
# print(res)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BX'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BX.init(sv.settings_gl)

# res, pr = BX.open_order('market', 'GLMRUSDT', 'Buy',20, False)
# print(res, pr)
# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BG'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BG.init(sv.settings_gl)

# res, pr = BG.open_order('market', 'SUIUSDT', 'Buy',20, True, 15.6)
# print(res, pr)
# coin = 'XRPUSDT'
# coin_list = BG.client.mix_get_symbols_info('UMCBL')
# for coin_info in coin_list['data']:
#     if coin_info['symbol'] == f'{coin}_UMCBL':
#         print(coin_info)
sv.settings_gl = Settings()
sv.settings_gl.exchange = 'BN'
sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
BN.init(sv.settings_gl)

res, contr = BN.is_contract_exist('BSVUSDT')
print(res)
if 'BSVUSDT' in contr:
    print('çontract exist')

# res, pt = BN.open_order('market', 'GALUSDT', 'Sell', 20, False)
# print(res, pt)
# res = BN.open_SL('market', 'GALUSDT', 'Sell', 10, 1.9245, 0.0001)
# res = BN.get_symbol_info('GALUSDT')
# print(res)
# res, contracts = BN.is_contract_exist('BTCUSDT')
# print(res)
# print('------------------------------------')
# print(contracts)
# res = BN.get_position('SOLUSDT')
# print(res)
# res = BN.get_balance()
# print(f'api status: {res}')
# res = BN.open_order('limit', 'AAVEUSDT', 'Buy', 20, False)
# print(res)
# coin_info = BN.get_symbol_info('ADAUSDT')
# print(float('0.0') == 0)
# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'OK'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# OKX.init(sv.settings_gl)

# # OKX.get_instrument_info('XRPUSDT')
# res, pr = OKX.open_order('market', 'GALUSDT', 'Sell', 20, False)
# print(res, pr)


# position = OKX.get_position('GALUSDT')
# print(position)
# amount_coin = ex.get_position_lots(position)
# print(amount_coin)
# pr = OKX.open_SL('GALUSDT', 'Sell', amount_coin, 1.9138085999999999, 0.005)
# print(pr)

# res, cont = OKX.is_contract_exist('GLMRUSDT')
# print(res, cont)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'GT'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# GT.init(sv.settings_gl)

# ord_id, pr = GT.open_order('KLAYUSDT', 'Sell', 20, False)
# print(ord_id, pr)
# pos = GT.get_position('KLAYUSDT')
# print(pos)
# ord_id = GT.open_SL('KLAYUSDT', 'Sell', -88, 0.2268, 0.004)
# print(ord_id)
# position = GT.get_position('DOTUSDT')
# print(position)
# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'KC'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# KuCoin.init(sv.settings_gl)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BB'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BB.init(sv.settings_gl)


# acc = BB.instrument_info('KLAYUSDT')
# print(acc)
# res, pr = BB.open_order('market', 'KLAYUSDT', 'Buy', 20, False)
# print(res, pr)

# BB.open_SL('market', 'KLAYUSDT', 'Buy', 88, 0.22612261, 0.004)
# res, contracts = BB.is_contract_exist('SOLUSDT')
# print(res)
# print('------------------------------------')
# print(contracts)
# res, list_1 = BB.is_contract_exist('XRPUSDT')
# res, list_2 = BN.is_contract_exist('XRPUSDT')
# res, list_3 = BG.is_contract_exist('XRPUSDT')
# res, list_4 = BM.is_contract_exist('XRPUSDT')
# res, list_5 = OKX.is_contract_exist('XRPUSDT')
# res, list_6 = KuCoin.is_contract_exist('XRPUSDT')
# res, list_7 = GT.is_contract_exist('XRPUSDT')
# res, list_8 = BX.is_contract_exist('XRPUSDT')

# result_list = serv.find_common_elements(list_1, list_2, list_3, list_4, list_5, list_6, list_7, list_8)
# print(len(result_list))
# for result in result_list:
#     print(result)