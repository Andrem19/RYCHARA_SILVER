import threading
from models.settings import Settings
from commander.com import Commander

time_format = "%Y-%m-%d %H:%M:%S"
settings_gl: Settings = Settings()
global_var_lock = threading.Lock()
commander: Commander = None
coins_in_work = {}
countet_live = 0


last_command = ''

manager_instance = 0
# exchanges_positions_limit = {}
exchanges_info = []

coin_last_take = {
    
}
coin_last_close = {
    
}
high_vol = False

position_was_close = False


messages_queue = []

best_set = [
  'ETHUSDT', 
   'DOTUSDT', 
    'ADAUSDT', 
    'XRPUSDT', 
    'LINKUSDT', 
    'MATICUSDT', 
    'UNIUSDT',
    'ATOMUSDT', 
    'FILUSDT', 
    'VETUSDT', 
    'ALGOUSDT', 
    'FTMUSDT', 
   'KAVAUSDT', 
    'GALAUSDT', 
    'DOGEUSDT',
    'SOLUSDT',
    'AVAXUSDT',
    'HBARUSDT',
    'QNTUSDT',
    'APTUSDT',
    'ARBUSDT',
    'GRTUSDT',
    'SNXUSDT',
    'STXUSDT',
    'EOSUSDT',
    'SANDUSDT',
    'INJUSDT',
    'RNDRUSDT',
    'NEOUSDT',
    'FLOWUSDT',
    'APEUSDT',
    'KLAYUSDT',
    'FXSUSDT',
    'MINAUSDT',
    'CRVUSDT',
    'SUIUSDT',
    'DASHUSDT',
    'CFXUSDT',
    'IOTAUSDT',
    'SUSHIUSDT',
    'OPUSDT',
    'BATUSDT',
    '1INCHUSDT',
    'TWTUSDT',
    'ARPAUSDT',
    'SKLUSDT',
    'ZILUSDT',
    'HOTUSDT',
    'AGIXUSDT',
    'COMPUSDT',
    'GLMRUSDT',
    'QTUMUSDT',
    'TRBUSDT',
    'MASKUSDT',
    "SSVUSDT",
    "STORJUSDT",
    "ICPUSDT",
    "MEMEUSDT",
    "ENSUSDT",
    "WOOUSDT",
    "BSVUSDT",
    "GMTUSDT",
    "RVNUSDT",
    "GALUSDT",
    "LDOUSDT",
    "WAVESUSDT",
    "MKRUSDT",
    "PYTHUSDT",
    "MAGICUSDT",
    "KSMUSDT",
    "FETUSDT",
    ]