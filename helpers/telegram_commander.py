import shared_vars as sv
from commander.com import Commander
from managers_func import *
import os
import traceback
from exchange_workers.kucoin import KuCoin
from exchange_workers.okx import OKX
from exchange_workers.bybit import BB
from exchange_workers.gate import GT
from exchange_workers.binance import BN
from exchange_workers.bitget import BG
from exchange_workers.bitmart import BM
from exchange_workers.bingx import BX
from exchange_workers.blofin.blofin import BF
from exchange_workers.phemex.phemex import PM
from exchange_workers.xt import XT
from models.settings import Settings


def close_all_position(coin: str, amt: float, sd: str, exchange: str):
    try:
        if exchange =='BB':
            BB.open_order('market', coin, sd, 2, True)
        elif exchange == 'KC':
            KuCoin.close_position_market(coin, sd)
        elif exchange == 'OK':
            OKX.open_order('market', coin, sd, 400, True)
        elif exchange == 'BG':
            BG.open_order('market', coin, sd, 2, True, amt)
        elif exchange == 'BX':
            BX.open_order('market', coin, sd, 2, True, amt)
        elif exchange == 'BM':
            BM.open_order('market', coin, sd, 2, True, amt)
        elif exchange == 'BN':
            BN.open_order('market', coin, sd, 2, True, amt)
        elif exchange == 'BF':
            BF.open_market_order(coin, sd, 2, True, amt)
        elif exchange == 'XT':
            XT.open_market_order(coin, sd, 2, True, amt)
        elif exchange == 'PM':
            PM.open_market_order(coin, sd, 2, True, 0.001, amt)
    except Exception as e:
        print(f'Error [close_all_position] {datetime.now()}] {e}')
        print(traceback.format_exc())

def get_exchange_positions():
   bn_pos = BN.is_any_position_exists()
   time.sleep(0.2)
   bb_pos = BB.is_any_position_exists()
   time.sleep(0.2)
   bg_pos = BG.is_any_position_exists()
   time.sleep(0.2)
   bm_pos = BM.is_any_position_exists()
   time.sleep(0.2)
   okx_pos = OKX.is_any_position_exists()
   time.sleep(0.2)
   kc_pos = KuCoin.is_any_position_exists()
   time.sleep(0.2)
   gt_pos = GT.is_any_position_exists()
   time.sleep(0.2)
   bx_pos = BX.is_any_position_exists()
   time.sleep(0.2)
   bf_pos = BF.is_any_position_exists()
   time.sleep(0.2)
   xt_pos = XT.is_any_position_exists()
   time.sleep(0.2)
   pm_pos = PM.is_any_position_exists()

   report = {
       'BN': bn_pos,
       'BB': bb_pos,
       'BG': bg_pos,
       'BM': bm_pos,
       'OK': okx_pos,
       'KC': kc_pos,
       'GT': gt_pos,
       'BX': bx_pos,
       'PM': pm_pos,
       'XT': xt_pos,
       'BF': bf_pos,
   }
   
   return report

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
        sv.settings_gl.exchange = 'PM'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        PM.init(sv.settings_gl)
        sv.settings_gl.exchange = 'XT'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        XT.init(sv.settings_gl)
        sv.settings_gl.exchange = 'BF'
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        BF.init(sv.settings_gl)

        report = get_exchange_positions()
        await tel.send_inform_message('WORKER_BOT', f'{report}', '', False)

        for key, val in report.items():
            if len(val)> 0:
                for pos in val:
                    trigger = True
                    close_all_position(pos[0], pos[2], pos[1], key)
                    RD.delete_one_field(f'exs_pos:{key}_{sv.manager_instance}', pos[0])
                    time.sleep(0.5)
        if trigger:
            report = get_exchange_positions()
            await tel.send_inform_message('WORKER_BOT', f'All position was close:\n{report}', '', False)
    except Exception as e:
        print(f'Error [check_and_close_all]: {e}')

async def balance(trsh: str = '0'):
    treshold = int(trsh)
    profit = 0
    exchanges = {
       'BN': BN,
       'BB': BB,
       'BG': BG,
       'BM': BM,
       'OK': OKX,
       'KC': KuCoin,
       'BX': BX,
       'PM': PM,
       'XT': XT,
       'BF': BF,
   }
    full_balance = 0
    report = {}
    for key, val in exchanges.items():
        sv.settings_gl.exchange = key
        sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
        sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
        val.init(sv.settings_gl)
        bal = float(val.get_balance())
        full_balance+=bal
        report[key] = round(bal, 2)

    profit = full_balance - treshold
    print(f'{report}\nProfit: {round(profit, 2)}')
    await tel.send_inform_message('WORKER_BOT', f'{report}\nFull balance: {round(full_balance, 2)}\nProfit: {round(profit, 2)}', '', False)


def init_commander():
    sv.commander = Commander(logs=True)

    sv.commander.add_command(["kill"], kill_proc)
    sv.commander.add_command(["start"], start_main_1)
    sv.commander.add_command(["balance"], balance)
    sv.commander.add_command(["amount", "all"], amount_all)
    sv.commander.add_command(["amount", "ex"], amount_ex)
    sv.commander.add_command(["close", "all"], check_and_close_all)
    sv.commander.add_command(["info"], info)
    
