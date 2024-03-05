import shared_vars as sv
from commander.com import Commander
from managers_func import *
import os
from exchange_workers.kucoin import KuCoin
from exchange_workers.okx import OKX
from exchange_workers.bybit import BB
from exchange_workers.gate import GT
from exchange_workers.binance import BN
from exchange_workers.bitget import BG
from exchange_workers.bitmart import BM
from exchange_workers.bingx import BX
from models.settings import Settings


async def kill_proc(*params):
    try:
        print(params)
        if len(params)== 0:
            await kill_processes(read_pids_from_file('process_pids.txt'))
            os.remove('process_pids.txt')
        else:
            print(params)
            ex = str(params[0])
            pids = read_pids_and_labels_from_file('process_pids.txt')
            for p in pids:
                print(p)
                pid = p.split(':')
                
                if pid[-1].lower() == ex.lower():
                    os.kill(int(pid[0]), 9)
                    msg = f"Process with PID {pid} killed successfully"
                    await tel.send_inform_message('WORKER_BOT', msg, '', False)
    except OSError as e:
        print(f"Failed to kill processes: {e}")

async def start_main_1():
    await run_signals()


async def info():
    await tel.send_inform_message('WORKER_BOT', sv.commander.show_tree(), '', False) 

async def amount_all(amount: str):
    am = float(amount)
    RD.rewrite_one_field('settings:worker', 'max_amount', am)
    time.sleep(0.1)
    max_amount = RD.read_dict_field('settings:worker', 'max_amount')
    await tel.send_inform_message('WORKER_BOT', f'New max amount for all workers is {max_amount}', '', False) 

async def amount_ex(ex: str, amount: str):
    am = float(amount)
    exchange = f'{ex.upper()}_{sv.manager_instance}'
    RD.rewrite_one_field(f'individual_settings:{exchange}', 'amount', am)
    time.sleep(0.1)
    max_amount = RD.read_dict_field(f'individual_settings:{exchange}', 'amount')
    await tel.send_inform_message('WORKER_BOT', f'New max amount for {exchange} workers is {max_amount}', '', False)

async def check_and_close_all():
    try:
        trigger = False
        sv.settings_gl = Settings()
        sv.settings_gl.exchange = 'BB'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        BB.init(sv.settings_gl)
        sv.settings_gl.exchange = 'KC'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        KuCoin.init(sv.settings_gl)
        sv.settings_gl.exchange = 'OK'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        OKX.init(sv.settings_gl)
        sv.settings_gl.exchange = 'BG'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        BG.init(sv.settings_gl)
        sv.settings_gl.exchange = 'BX'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        BX.init(sv.settings_gl)
        sv.settings_gl.exchange = 'BM'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        BM.init(sv.settings_gl)
        sv.settings_gl.exchange = 'GT'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        GT.init(sv.settings_gl)
        sv.settings_gl.exchange = 'BN'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        BN.init(sv.settings_gl)

        report = serv.get_exchange_positions()
        await tel.send_inform_message('WORKER_BOT', f'{report}', '', False)

        for key, val in report.items():
            if len(val)> 0:
                for pos in val:
                    trigger = True
                    serv.close_all_position(pos[0], pos[2], pos[1], key)
                    time.sleep(0.5)
        if trigger:
            report = serv.get_exchange_positions()
            await tel.send_inform_message('WORKER_BOT', f'All position was close:\n{report}', '', False)
    except Exception as e:
        print(f'Error [check_and_close_all]: {e}')

def init_commander():
    sv.commander = Commander(logs=True)

    sv.commander.add_command(["kill"], kill_proc)
    sv.commander.add_command(["start"], start_main_1)
    sv.commander.add_command(["amount", "all"], amount_all)
    sv.commander.add_command(["amount", "ex"], amount_ex)
    sv.commander.add_command(["close", "all"], check_and_close_all)
    sv.commander.add_command(["info"], info)
    
