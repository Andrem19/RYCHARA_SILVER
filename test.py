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

common_coins = [
    "MEMEUSDT",
    "OPUSDT",
    "CHZUSDT",
    "ETHUSDT",
    "INJUSDT",
    "TRBUSDT",
    "GALUSDT",
    "BNTUSDT",
    "ORBSUSDT",
    "THETAUSDT",
    "EGLDUSDT",
    "MANAUSDT",
    "ZRXUSDT",
    "SUSHIUSDT",
    "ORDIUSDT",
    "MAGICUSDT",
    "NEOUSDT",
    "LDOUSDT",
    "SNXUSDT",
    "AGIXUSDT",
    "FLMUSDT",
    "MASKUSDT",
    "WOOUSDT",
    "PEOPLEUSDT",
    "XLMUSDT",
    "ADAUSDT",
    "MKRUSDT",
    "ICPUSDT",
    "LRCUSDT",
    "APTUSDT",
    "MINAUSDT",
    "DYDXUSDT",
    "ACEUSDT",
    "SSVUSDT",
    "RNDRUSDT",
    "BLURUSDT",
    "TRXUSDT",
    "ATOMUSDT",
    "STORJUSDT",
    "XRPUSDT",
    "LINKUSDT",
    "GRTUSDT",
    "ARBUSDT",
    "SANDUSDT",
    "CRVUSDT",
    "AGLDUSDT",
    "PYTHUSDT",
    "TIAUSDT",
    "AXSUSDT",
    "DOGEUSDT",
    "BCHUSDT",
    "KNCUSDT",
    "WAXPUSDT",
    "GMTUSDT",
    "AVAXUSDT",
    "CFXUSDT",
    "SOLUSDT",
    "FILUSDT",
    "WAVESUSDT",
    "IDUSDT",
    "SUIUSDT",
    "BIGTIMEUSDT",
    "FLOWUSDT",
    "APEUSDT",
    "MATICUSDT",
    "GALAUSDT",
    "ALGOUSDT",
    "STXUSDT",
    "FETUSDT",
    "FTMUSDT",
    "BNBUSDT",
    "WLDUSDT",
    "AAVEUSDT",
    "COMPUSDT",
    "ENSUSDT",
    "JTOUSDT",
    "1INCHUSDT",
    "NEARUSDT",
    "KSMUSDT",
    "ETCUSDT",
    "EOSUSDT",
    "DOTUSDT",
    "UNIUSDT",
    "ZILUSDT",
    "BSVUSDT",
    "RVNUSDT",
    "LTCUSDT"
]
all_coins = [
  'ETHUSDT', 
   'DOTUSDT', 
   'BNBUSDT', 
    'ADAUSDT', 
   'BTCUSDT', 
    'XRPUSDT', 
    'LINKUSDT', 
    'MATICUSDT', 
    'UNIUSDT',
    'ATOMUSDT', 
    'FILUSDT', 
    'VETUSDT', 
    'ALGOUSDT', 
    'FTMUSDT', 
    'MANAUSDT', 
   'KAVAUSDT', 
    'GALAUSDT', 
    'DYDXUSDT',
    'DOGEUSDT',
    'SOLUSDT',
    'TRXUSDT',
    'LTCUSDT',
    'XLMUSDT',
    'AVAXUSDT',
    'XMRUSDT',
    'HBARUSDT',
    'QNTUSDT',
    'APTUSDT',
    'ARBUSDT',
    'AAVEUSDT',
    'GRTUSDT',
    'SNXUSDT',
    'STXUSDT',
    'EOSUSDT',
    'EGLDUSDT',
    'SANDUSDT',
    'THETAUSDT',
    'INJUSDT',
    'RNDRUSDT',
    'AXSUSDT',
    'NEOUSDT',
    'RUNEUSDT',
    'FLOWUSDT',
    'APEUSDT',
    'CHZUSDT',
    'KLAYUSDT',
    'FXSUSDT',
    'MINAUSDT',
    'CRVUSDT',
    'SUIUSDT',
    'DASHUSDT',
    'CFXUSDT',
    'IOTAUSDT',
    'LUNAUSDT',
    'LUNCUSDT',
    'SUSHIUSDT',
    'ORDIUSDT',
    'OPUSDT',
    'TIAUSDT',
    'KASUSDT',
    'SHIBUSDT',
    'BATUSDT',
    'ARUSDT',
    'BLURUSDT',
    'ILVUSDT',
    'GMXUSDT',
    '1INCHUSDT',
    'TWTUSDT',
    'ARPAUSDT',
    'SKLUSDT',
    'ZILUSDT',
    'HOTUSDT',
    'GASUSDT',
    'AGIXUSDT',
    'COMPUSDT',
    'GLMRUSDT',
    'QTUMUSDT',
    'LRCUSDT',
    'TRBUSDT',
    'MASKUSDT',
    'ENJUSDT'
    ]

def elements_in_second_not_in_first(list1, list2):
    # Используем множества для упрощения операций
    set1 = set(list1)
    set2 = set(list2)

    # Находим элементы, которые есть во втором списке, но нет в первом
    unique_to_list2 = set2.difference(set1)

    # Преобразуем результат обратно в список
    unique_elements = list(unique_to_list2)

    return unique_elements

result = elements_in_second_not_in_first(all_coins, common_coins)
print(len(result))
for res in result:
    print(res)