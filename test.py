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
import requests
import json
from datetime import datetime
import time
from helpers.redisdb import RD
RD.initialize()
serv.change_rating_redis('ADAUSDT', 1)
# def event_handler(message):
#     print('Event received:', message)
# def run_listner():
#     RD.initialize()

#     pubsub = RD._client.pubsub()
#     pubsub.psubscribe(**{"__keyspace@0__:trigger": event_handler})
#     thread = pubsub.run_in_thread(sleep_time=0.01)
# RD.initialize()
# last_saldo = serv.get_last_saldo('BN_1')
# print(last_saldo)
    # while True:
    #     time.sleep(3)
    #     print('loop')
# run_listner()
# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BM'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BM.init(sv.settings_gl)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BX'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BX.init(sv.settings_gl)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BG'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BG.init(sv.settings_gl)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BN'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BN.init(sv.settings_gl)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'OK'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# OKX.init(sv.settings_gl)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'GT'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# GT.init(sv.settings_gl)

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