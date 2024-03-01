import shared_vars as sv
from commander.com import Commander
from managers_func import *
import os



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

def init_commander():
    sv.commander = Commander(logs=True)

    sv.commander.add_command(["kill"], kill_proc)
    sv.commander.add_command(["start"], start_main_1)
    sv.commander.add_command(["amount", "all"], amount_all)
    sv.commander.add_command(["amount", "ex"], amount_ex)
    sv.commander.add_command(["info"], info)
    
