import subprocess
from telegram import Bot
from decouple import config
import time
import helpers.telegr as tel
import helpers.firebase as fb
import shared_vars as sv
import os
from helpers.redisdb import RD
import platform
import bot_commands as bc
from datetime import datetime
import helpers.services as serv

old_timestamp = 0

api_token = None

def start_program(i: int, exchange: str):
    python_command = ['python3', '-u'] if platform.system() == 'Linux' else ['python', '-u']
    subprocess.Popen(python_command + ['main.py', str(i), exchange], stdout=open(f'output{exchange}{i}.log', 'w'), stderr=subprocess.STDOUT)


async def run_signals():
    process_pids = []
    labels = []
    sv.exchanges_info = RD.load_all_key('individual_settings')

    for val in sv.exchanges_info:
        if sv.manager_instance == int(val['inst']) and int(val['status'])==1:
            start_program(val['inst'], val['ex'])
            labels.append(val['ex'])
            print('sleep 5')
            await tel.send_inform_message('WORKER_BOT', f'{val["ex"]}-{val["inst"]} running!', '', False)
            time.sleep(5)

    print('sleep 5')
    time.sleep(5)

    # Находим PID процессов с именем 'main.py'
    for pid in os.listdir('/proc'):
        try:
            pid = int(pid)
            cmdline = open(os.path.join('/proc', str(pid), 'cmdline'), 'rb').read().decode('utf-8')
            if 'python3' in cmdline and 'main.py' in cmdline:
                process_pids.append(pid)
        except (ValueError, FileNotFoundError, IOError):
            print(IOError)
            continue

    # Записываем PID в файл#
    print('Записываем PID в файл')
    write_pids_to_file('process_pids.txt', process_pids, labels)

    print(f"Запущено {len(process_pids)} процессов с PID: {process_pids}")


def write_pids_to_file(filename, pids, labels):
    with open(filename, 'w') as file:
        for pid, label in zip(pids, labels):
            file.write(f"{pid}:{label}\n")

# def read_pids_from_file(filename):
#     with open(filename, 'r') as file:
#         pids = [int(pid.strip()) for pid in file.readlines()]
#     return pids
def read_pids_from_file(filename):
    with open(filename, 'r') as file:
        pids = [int(line.split(':')[0].strip()) for line in file.readlines()]
    return pids

def read_pids_and_labels_from_file(filename):
    with open(filename, 'r') as file:
        pid_label_pairs = [line.strip() for line in file.readlines()]
    return pid_label_pairs

async def kill_processes(pids):
    for pid in pids:
        try:
            os.kill(pid, 9)  # Sends a SIGKILL signal to the process
            msg = f"Process with PID {pid} killed successfully"
            await tel.send_inform_message('WORKER_BOT', msg, '', False)
            print(msg)
        except OSError:
            print(f"Failed to kill process with PID {pid}")

async def watchgdog():
    try:
        alives = []
        for val in sv.exchanges_info:
            print(val['inst'], val['status'])
            if sv.manager_instance == int(val['inst']) and int(val['status'])==1:
                inst_time_val = RD.get_val(f'watchdog:worker:{val["ex"]}_{val["inst"]}')
                print(inst_time_val, f'watchdog:{val["ex"]}_{val["inst"]}')
                if inst_time_val is None:
                    print('[watchgdog] istance doesnt exist')
                    return
                timestamp = float(inst_time_val)
                if timestamp +300 < datetime.now().timestamp():
                    await kill_processes(read_pids_from_file('process_pids.txt'))
                    os.remove('process_pids.txt')
                    alives.append(False)
                    time.sleep(3)
                    await run_signals()
                else:
                    alives.append(True)
        if all(alives):
            print('send alive')
            # error_status = RD.get_val('error:')
            await bc.alive('WORKER_BOT')
        else:
            print('send not alive')
            await tel.send_inform_message('WORKER_BOT', f'Somthing wrong... Not all process alive!', '', False)
    except Exception as e:
        print(str(e))



async def check_process_pids():
    if not os.path.exists('process_pids.txt'):
        return
    pids = read_pids_from_file('process_pids.txt')

    for pid in pids:
        try:
            os.kill(pid, 0)  # Check if process exists
        except OSError:
            await kill_processes(read_pids_from_file('process_pids.txt'))
            os.remove('process_pids.txt')
            await run_signals()



    
async def check_and_handle_message():
    global old_timestamp, api_token
    try:
        bot = Bot(token=api_token)

        updates = await bot.get_updates()
        message = None
        if len(updates) > 0:
            message = updates[-1].message
        else: 
            return
        if message is not None and old_timestamp != message.date.timestamp() and (time.time() - message.date.timestamp()) <= 30:
            old_timestamp = message.date.timestamp()
            await sv.commander.exec_command(message.text)

    except Exception as e:
        import traceback
        print(f'Error [check_and_handle_message]: {e}')
        print(f"Exception type: {type(e)}")
        print(traceback.format_exc())

# async def check_and_handle_message():
#     global old_timestamp, api_token
#     try:
#         # Create a Telegram bot instance
#         bot = Bot(token=api_token)

#         # Get the latest message from the bot's chat
#         updates = await bot.get_updates()
#         message = ''
#         if len(updates) > 0:
#             message = updates[-1].message
#         else: 
#             return
#         # Check if there is a new message
#         if message is not None and old_timestamp != message.date.timestamp() and (time.time() - message.date.timestamp()) <= 30:
#             old_timestamp = message.date.timestamp()
#             sv.last_command = message.text
#             if message.text == 'kill' or message.text == 'Kill':
#                 await kill_processes(read_pids_from_file('process_pids.txt'))
#                 os.remove('process_pids.txt')
#             if message.text =='restart' or message.text == 'Restart':
#                 await kill_processes(read_pids_from_file('process_pids.txt'))
#                 os.remove('process_pids.txt')
#                 await run_signals()
#             if message.text =='start' or message.text == 'Start':
#                 await run_signals()
            # if message.text =='pids' or message.text == 'Pids':
            #     pids = read_pids_and_labels_from_file('process_pids.txt')
            #     msg = ''
            #     for p in pids:
            #         msg += f'{p}\n'
            #     await tel.send_inform_message('WORKER_BOT', msg, '', False)
#             print("New message handled successfully!")
#     except Exception as e:
#         print("An error occurred:", str(e))