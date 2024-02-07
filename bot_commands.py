from telegram import Update, Bot
import helpers.telegr as tel
from decouple import config
from telegram.ext import ContextTypes
import helpers.services as serv
import helpers.visualizer as vis
from models.settings import Settings
from models.position import Position
import helpers.firebase as fb
import shared_vars as sv
import random
import facts as fc



# async def request(request: str, settings: Settings):
#     commands = request.split(' ')
#     if commands[0] == 'tr' or commands[0] == 'Tr':
#         await trend(commands[1], settings)
#     if commands[0] == 'ph' or commands[0] == 'Ph':
#         await pos_history(commands[1], settings)
#     if commands[0] == 'gs' or commands[0] == 'Gs':
#         await get_status(settings)
#     if commands[0] == 'ping' or commands[0] == 'Ping':
#         await alive(settings)
#     if commands[0] == 'stop' or commands[0] == 'Stop': # Stop DOTUSDT Sell 10
#         await close_order(settings, commands[1], commands[2], commands[3])

async def alive(api_token):
    msg = ''
    for k, v in sv.coins_in_work.items():
        msg += f'{k}: {v}\n'
    if msg == '':
        msg += random.choice(fc.words)
    await tel.send_inform_message(api_token, f'{msg}', '', False)

# async def get_status(date_str: str, settings: Settings):
#     res = fb.read_data('status', 'entitys')
#     await tel.send_inform_message(settings.telegram_token, f'status: {res[settings.name]}', '', False)


# async def trend(date_str: str, settings: Settings):
#     saldos = sal.load_saldo()
#     filtered_saldos = serv.filter_list_by_timestamp(saldos, serv.convert_to_timestamp(date_str))
#     path = vis.plot_time_series(filtered_saldos, True, settings.border_saldo)
#     await tel.send_inform_message(settings.telegram_token, f'{settings.coin}-{settings.exchange}', path, True)

# async def pos_history(number: str, settings: Settings):
#     num = int(number)
#     possitions = serv.read_deser_positions(settings.coin)
#     if num > 2:
#         await tel.send_inform_message(settings.telegram_token, 'You cant load more then 2 possition', '', False)
#     else:
#         res_pos = possitions[-num:]
#         await tel.send_inform_message(settings.telegram_token, Position.parse_to_pretty_string(res_pos), '', False)
    
# async def close_order(settings: Settings, coin, bs, amount):
#     res = BybitAPI.place_close_order(coin, bs, int(amount))
#     await tel.send_inform_message(settings.telegram_token, str(res), '', False)

     