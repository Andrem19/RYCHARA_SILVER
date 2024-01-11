import threading
from models.settings import Settings

time_format = "%Y-%m-%d %H:%M:%S"
settings_gl: Settings = Settings()
global_var_lock = threading.Lock()
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