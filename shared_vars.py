import threading
from models.settings import Settings

time_format = "%Y-%m-%d %H:%M:%S"
settings_gl: Settings = Settings()
global_var_lock = threading.Lock()
coins_in_work = {}
countet_live = 0




manager_instance = 0
exchanges_positions_limit = {
    'KC_1': {'numbers': 5, 'amount': 200, 'status': 1, 'ex': 'KC', 'inst': 1},
    'OK_1': {'numbers': 5, 'amount': 200, 'status': 1, 'ex': 'OK', 'inst': 1},
    'BG_1': {'numbers': 5, 'amount': 200, 'status': 1, 'ex': 'BG', 'inst': 1},
    'BT_1': {'numbers': 5, 'amount': 200, 'status': 1, 'ex': 'BT', 'inst': 1},
    'DF_1': {'numbers': 5, 'amount': 200, 'status': 1, 'ex': 'DF', 'inst': 1},
    'BB_1': {'numbers': 5, 'amount': 200, 'status': 0, 'ex': 'BB', 'inst': 1},
}

exclude_okx = [
    'KAVAUSDT',
    'QNTUSDT',
    'XMRUSDT',
]
exclude_kc = [

]
exclude_bg = [

]
exclude_bx = [

]
exclude_bm = [

]
exclude_gt = [

]
exclude_bb = [

]
exclude_bn = [

]
coin_last_take = {
    
}
coin_last_close = {
    
}
high_vol = False

position_was_close = False