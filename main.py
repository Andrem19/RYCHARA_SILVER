import shared_vars as sv
import asyncio
from models.settings import Settings
from exchange_workers.bybit import BB
from exchange_workers.kucoin import KuCoin
from exchange_workers.bitget import BG
from exchange_workers.okx import OKX
from exchange_workers.bitmart import BM
from exchange_workers.bingx import BX
from exchange_workers.binance import BN
from exchange_workers.gate import GT
from exchange_workers.xt import XT
from exchange_workers.blofin.blofin import BF
from exchange_workers.phemex.phemex import PM
from helpers.redisdb import RD
import hendler as hn
from datetime import datetime
import traceback
import time
import helpers.telegr as tel
import sys

def re_init_global():
    if sv.settings_gl.exchange == 'BB':
        BB.re_init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'KC':
        KuCoin.re_init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'OK':
        OKX.re_init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BG':
        BG.re_init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BX':
        BX.re_init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BM':
        BM.re_init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'GT':
        GT.re_init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BN':
        BN.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BF':
        BF.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'XT':
        XT.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'PM':
        PM.init(sv.settings_gl)

def on_signal_change(message):
    signal_collection = RD.load_all_key('coin')
    # re_init_global()
    signals = hn.decision_maker(signal_collection)
    print(f'on_signal_change {datetime.now()}')
    if signals != -1:
        print(f'{len(signals)} coins')
        for sig in signals:
            hn.handler(sig)
            time.sleep(0.5)

def run_listner():
    pubsub = RD._client.pubsub()
    pubsub.psubscribe(**{"__keyspace@0__:trigger": on_signal_change})
    pubsub.run_in_thread(sleep_time=0.01)

async def main(args=None):
    if args is None:
        args = [1]

    RD.initialize()
    sv.settings_gl = Settings()

    set_dict = RD.read_dict('settings:worker')
    sv.settings_gl.from_dict(set_dict)

    argument1 = int(args[0])
    sv.settings_gl.name = f'{args[1]}_{argument1}'
    sv.settings_gl.exchange = args[1]
    sv.settings_gl.telegram_token = f'API_TOKEN_{args[1]}'
    sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{argument1}'
    sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{argument1}'

    RD.write_val(f'watchdog:worker:{sv.settings_gl.name}', datetime.now().timestamp())

    if sv.settings_gl.exchange == 'BB':
        BB.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'KC':
        KuCoin.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'OK':
        OKX.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BG':
        BG.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BX':
        BX.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BM':
        BM.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'GT':
        GT.init(sv.settings_gl)
    elif sv.settings_gl.exchange == 'BN':
        BN.init(sv.settings_gl)

    print(f'Settings load successfuly with arguments: {args}')
    run_listner()
    
    while True:
        try:
            if sv.countet_live%60==0:
                sv.countet_live=0
                with sv.global_var_lock:
                    RD.write_val(f'watchdog:worker:{sv.settings_gl.name}', datetime.now().timestamp())
                    if len(sv.coins_in_work) == 0:
                        sv.high_vol = False
            sv.countet_live+=1
            pos_was_close = False
            with sv.global_var_lock:
                if sv.position_was_close == True:
                    sv.position_was_close = False
                    pos_was_close = True
            if pos_was_close:
                pos_was_close = False
                # on_signal_change(None, None, None)
            await tel.send_queue()
            time.sleep(1)
        except Exception as e:
            print(f"Error [main while loop]: {e}")
            print(f"Exception type: {type(e)}")
            print(traceback.format_exc())
                
        


if __name__ == '__main__':
    # main(sys.argv[1:])
   asyncio.run(main(sys.argv[1:]))