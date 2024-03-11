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
from exchange_workers.phemex.phemex import PM
import exchange_workers.binance as b
import requests
import asyncio
import helpers.telegram_commander as com
import exchange_workers.exchanges as ex
from decouple import config
import json
from datetime import datetime
import time
from exchange_workers.xt import XT
from helpers.redisdb import RD
from exchange_workers.blofin.blofin import BF
# PMAPI_1=2e1ab653-b607-4f78-9cee-e7bbeec384d9
# PMSECRET_1=FydpbH3TVB07pyOecx8OGOR9kKy0hoSkmzPrbSYDTxFmNjc2ZjAyYS1jOGNhLTRiNmEtYTE3MS04NWQwYTM1MWMzYTA

sv.settings_gl = Settings()
sv.settings_gl.exchange = 'PM'
sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
PM.init(sv.settings_gl)


res, ord = PM.open_market_order('DOTUSDT', 'Sell', 20, True, 0.004, 32)
print(res, ord)
# res = PM.get_position('XRPUSDT')
# print(res)
# res = PM.open_SL('XRPUSDT', 'Buy', 31, 0.6254, 0.005)
# res = PM.get_position('XRPUSDT')
# print(res)
# num = 0
# for cn in sv.best_set:
#     if cn not in contracts:
#         num+=1
#         print(num, cn)
# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'XT'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# XT.init(sv.settings_gl)

# res, ord = XT.open_market_order('XRPUSDT', 'Sell', 20, True, 3)
# print(res, ord)
# position = XT.get_position('XRPUSDT', 2)
# print(position)
# res = XT.open_SL('XRPUSDT', 'Sell', 3, 0.6127, 0.005)
# print(res)
# XT.cancel_all_orders('XRPUSDT')
# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BF'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BF.init(sv.settings_gl)

# res = BF.get_balance()
# res, ord = BF.open_market_order('DOTUSDT', 'Buy', 20, True, 1)
# print(res, ord)
# res = BF.get_position('DOTUSDT')
# print(res)
# res = BF.open_SL('DOTUSDT', 'Buy', 1, 10.331, 0.005)
# print(res)
# BF.cancel_all_orders('DOTUSDT', True)
# res = DC.open_order('limit', 'XRPUSDT', 'Buy', 20, False)
# print(res)
# num = 0
# for cn in sv.best_set:
#     if cn not in contracts:
#         num+=1
#         print(num, cn)



# sv.manager_instance = 1
# asyncio.run(com.check_and_close_all())
# RD.initialize()
# coin = 'XRPUSDT'
# c = f'{coin[:-4]}-{coin[-4:]}'
# print(c)

# def convert_name(name: str):
#     res = name.split('-')
#     return f'{res[0]}{res[1]}'

# res = convert_name(c)
# print(res)

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

# res = BM.is_any_position_exists()
# print(res)
# res = BM.get_position('XRPUSDT')
# print(res)

# res = BM.client.post_submit_leverage('ZILUSDT', 'cross', '20')
# print(res)
# res, ord = BM.open_order('market', 'ZILUSDT', 'Buy', 20, False)
# print(res, ord)
# response = requests.get(f'https://api-cloud.bitmart.com/contract/public/details?symbol=ZILUSDT')
# res = response.json()
# print(res)
# BM.client.post_submit_leverage()

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BX'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BX.init(sv.settings_gl)


# BX.is_any_position_exists()
# coin = 'ZILUSDT'
# c = f'{coin[:-4]}-{coin[-4:]}'
# res = BX.client.switch_leverage(symbol=c, side='LONG', leverage='20')
# print(res)

# contracts = BX.client.contracts()
# for cont in contracts:
#     if cont['symbol'] == c:
#         print(cont)
# contracts = BX.client.switch_margin_mode(c, 'CROSSED')
# contracts = BX.client.margin_mode(c)
# contracts = BX.client.switch_leverage(c, 'LONG', 20)
# contracts = BX.client.leverage(c)
# print(contracts)

# res, pr = BX.open_order('market', coin, 'Buy',20, False)
# print(res, pr)

# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BG'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BG.init(sv.settings_gl)

# res = BG.is_any_position_exists()
# print(res)
# res, pr = BG.open_order('market', 'SUIUSDT', 'Buy',20, True, 15.6)
# print(res, pr)
# coin = 'XRPUSDT'
# coin_list = BG.client.mix_get_symbols_info('UMCBL')
# for coin_info in coin_list['data']:
#     if coin_info['symbol'] == f'{coin}_UMCBL':
#         print(coin_info)
# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BN'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BN.init(sv.settings_gl)

# res =BN.is_any_position_exists()
# print(res)
# res = BN.client.change_leverage('MKRUSDT', 20)
# print(res)

# res, contr = BN.is_contract_exist('BSVUSDT')
# print(res)
# if 'BSVUSDT' in contr:
#     print('çontract exist')

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

# res = OKX.is_any_position_exists()
# print(res)
# res = OKX.get_instrument_info('ETHUSDT')
# print(res)
# coin = 'GMTUSDT'
# c = f'{coin[:-4]}-{coin[-4:]}'
# res = OKX.accountAPI.set_leverage(lever='20', mgnMode='cross', instId=f'{c}-SWAP', ccy='USDT')
# print(res)


# res, pr = OKX.open_order('market', 'GMTUSDT', 'Sell', 20, False)
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

# res = GT.is_any_position_exists()
# print(res)
# coin = 'XRPUSDT'
# c = f'{coin[:-4]}_{coin[-4:]}'
# cur_pr = GT.get_last_price(coin)
# pos = GT.open_SL(coin, 'Buy', 20, cur_pr, 0.006)
# print(pos)
# res = GT.get_balance()
# print(res)
# coin = 'ZILUSDT'
# c = f'{coin[:-4]}_{coin[-4:]}'
            
# contract = GT.futures_api.get_futures_contract('usdt', c)
# print(contract)

# ord_id, pr = GT.open_order('TRBUSDT', 'Sell', 20, False)
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

# res = KuCoin.is_any_position_exists()
# print(res)
# coin = 'ZILUSDT'
# contract_info = KuCoin.market_client.get_contract_detail(f'{coin}M')
# print(contract_info)
# KuCoin.open_market_order(coin, 'Buy', 20)
# sv.settings_gl = Settings()
# sv.settings_gl.exchange = 'BB'
# sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_1'
# sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_1'
# BB.init(sv.settings_gl)

# res = BB.is_any_position_exists()
# print(res)
# acc = BB.instrument_info('ZILUSDT')
# print(acc)


# acc = BB.instrument_info('KLAYUSDT')
# print(acc)
# BB.set_leverage('ZILUSDT', 20)
# res, pr = BB.open_order('market', 'ZILUSDT', 'Buy', 20, False)
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