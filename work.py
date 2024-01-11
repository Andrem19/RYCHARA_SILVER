from models.settings import Settings
from models.position import Position
import exchange_workers.exchanges as ex
from exchange_workers.bybit_http import BybitAPI
from google.api_core import datetime_helpers
import json
from helpers.redisdb import RD
import helpers.db as db
import helpers.firebase as fb
import helpers.telegr as tel
import helpers.services as ser
import helpers.firebase as fb
import helpers.profit as prof
import datetime
from datetime import timedelta
import helpers.services as serv
import shared_vars as sv
import traceback
import time
import copy
import helpers.visualizer as viz


async def open_position(settings: Settings, signal: int):
    try:
        close_order = False
        safe_tp_border, safe_ls_border = 0, 0
        target_len = settings.target_len
        print('start open position')
        time_start = datetime.datetime.now().timestamp()
        res, cur_pos = await ex.place_universal_order(settings, signal)
        if res:
            safe_ls_border = cur_pos.price_open * (1-settings.stop_loss) if signal == 1 else cur_pos.price_open * (1+settings.stop_loss)
            safe_tp_border = cur_pos.price_open * (1+settings.take_profit) if signal == 1 else cur_pos.price_open * (1-settings.take_profit)
        else:
            return await position_wasnt_open(settings)
        while res:
            try:
                time.sleep(settings.pause)
                last_price = ex.get_last_price(settings.coin)
                time_obj = datetime.datetime.strptime(cur_pos.time_open, sv.time_format)
                duration = datetime.datetime.now() - time_obj
                duration_seconds = duration.total_seconds()
                cur_pos.duration = duration_seconds
                res, responce = ex.is_position_exist(ex.get_position_info(settings.coin, signal))

                if duration_seconds >= target_len * 60 and not close_order and res:
                    print(f'[thread: {settings.my_uid}] Time: {datetime.datetime.now()} time to close')
                    ex.cancel_order(settings, cur_pos.order_sl_id, True)
                    cur_pos.order_sl_id = ex.close_limit_time_finish(settings, cur_pos, last_price)
                    cur_pos.price_close = last_price
                    time.sleep(8)
                    res, responce = ex.is_position_exist(ex.get_position_info(settings.coin, signal))
                    if res:
                        ex.cancel_order(settings, cur_pos.order_sl_id, True)
                        ex.close_time_finish(settings, cur_pos)
                        cur_pos.price_close = ex.get_last_price(settings.coin)
                        cur_pos.type_of_close = 'Market Time-Finish'
                    else:
                        cur_pos.type_of_close = 'Limit Time-Finish'
                    close_order = True
                
                if (last_price < safe_ls_border * (1-0.002) and signal == 1) or (last_price > safe_ls_border * (1+0.002) and signal == 2):
                    if not close_order and res:
                        print(f'[thread: {settings.my_uid}] Time: {datetime.datetime.now()} save closing market')
                        ex.close_time_finish(settings, cur_pos)
                        cur_pos.price_close = ex.get_last_price(settings.coin)
                        cur_pos.type_of_close = 'Market Safe_SL-Lim'
                        close_order = True
                if (last_price > safe_tp_border * (1+0.002) and signal == 1) or (last_price < safe_tp_border * (1-0.002) and signal == 2):
                    if not close_order and res:
                        print(f'[thread: {settings.my_uid}] Time: {datetime.datetime.now()} save closing market')
                        ex.close_time_finish(settings, cur_pos)
                        cur_pos.price_close = ex.get_last_price(settings.coin)
                        cur_pos.type_of_close = 'Market Safe_TP-Lim'
                        close_order = True
                
                if time_start + settings.message_timer < datetime.datetime.now().timestamp():
                    await handle_message(settings, responce, duration)
                    time_start = datetime.datetime.now().timestamp()
            except Exception as e:
                print(f'Error: {e}')
                await tel.send_inform_message(settings.telegram_token, f'Error [worker]: {datetime.datetime.now()} {e}', '', False)
                
        await handle_position(cur_pos, settings)

    except Exception as e:
        print(f"Error [handle_position]: {e}")
        print(f"Exception type: {type(e)}")
        print(traceback.format_exc())
        res, responce = ex.is_position_exist(ex.get_position_info(settings.coin, signal))
        if res:
            ex.close_time_finish(settings, cur_pos)
            await handle_position(cur_pos, settings)
        await tel.send_inform_message(settings.telegram_token, f'Error: {e}\n[worker {settings.coin}] All orders and position closed', '', False)
                
async def handle_message(settings: Settings, response: dict, duration):
    left = settings.target_len * 60 - duration.total_seconds()
    message = f'{settings.name} tf: {settings.timeframe} coin: {settings.coin}\nunrealisedPnl: {ex.get_unrealized_PNL(response)}\ntarg_len: {settings.target_len} duration: {duration}\nleft: {timedelta(seconds=left)}'
    print(message)
    await tel.send_inform_message(settings.telegram_token, message, '', None)

async def position_wasnt_open(settings: Settings):
    message = f'[thread: {settings.my_uid}] Position wasn\'t open'
    print(message)
    await tel.send_inform_message(settings.telegram_token, message, '', None)
    with sv.global_var_lock:
        sv.coins_in_work.pop(settings.coin)

async def handle_position(cur_pos: Position, settings: Settings):
    try:
        message = f'[thread: {settings.my_uid}] Handle position started'
        print(message)
        ex.cancel_all_orders(settings.coin, True, cur_pos.order_sl_id)
        # last_saldo = db.get_last_saldo()
        last_saldo = serv.get_last_saldo(settings.name)
        new_balance = ex.get_balance()
        cur_pos.new_balance = round(new_balance, 4)
        cur_pos.time_close = datetime.datetime.now().strftime(sv.time_format)
        profit = new_balance - cur_pos.old_balance
        cur_pos.profit = round(profit, 4)
        
        with sv.global_var_lock:
            sv.coins_in_work.pop(settings.coin)
            rating_val = -1 if cur_pos.profit < 0 else 2
            fb.change_rating(settings.coin, rating_val)
            print(f'[thread: {settings.my_uid}] rating was changed')
            sv.position_was_close = True

        

        cur_pos.duration = ser.convert_seconds_to_period(float(cur_pos.duration))
        if cur_pos.price_close == 0 and cur_pos.profit < 0:
            cur_pos.price_close = cur_pos.price_open * (1+settings.stop_loss) if cur_pos.signal == 2 else cur_pos.price_open * (1-settings.stop_loss)
        bs = True if cur_pos.signal == 1 else False
        cur_pos.profit_2 = prof.profit_counter(True, cur_pos.price_open, bs, cur_pos.price_close, settings.amount_usdt)
        new_saldo = last_saldo + profit
        saldo_dict = {
            'tm': datetime.datetime.now().timestamp(),
            'saldo': new_saldo
        }
        # db.add_saldo([datetime.datetime.now().timestamp()*1000, new_saldo], f'_db/saldo.txt')
        # db.add_pos_to_db(cur_pos, f'_db/history_pos.txt')
        
        RD.delete_one_field(f'exs_pos:{settings.name}', settings.coin)
        RD.add_val_to_list(f'saldo:{settings.name}', json.dumps(saldo_dict))
        RD.add_val_to_list(f'pos:{settings.name}', str(vars(cur_pos)))
        if cur_pos.profit < 0 and cur_pos.profit_2 < 0:
            RD.rewrite_one_field('increase_border', settings.coin, 12)

        icon = '✅'
        note = 'with profit'
        if cur_pos.profit_2 > 0 or cur_pos.profit > 0:
            icon = '✅'
            note = 'with profit'
        else:
            icon = '❌'
            note = 'with lose'
        await tel.send_inform_message(settings.telegram_token, f'{icon}Position was closed {note}: {str(cur_pos)}', '', None)
        time.sleep(1)
        await tel.send_inform_message(settings.collector_bot, f'{icon}Position was closed {note} {settings.name}: {str(cur_pos)}', '', None)
        if settings.exchange == 'KC':
            time.sleep(1)
            await viz.create_and_send_chart(settings, cur_pos.duration, cur_pos.signal, cur_pos.profit)
    except Exception as e:
        print(f"Error [handle_position]: {e}")
        print(f"Exception type: {type(e)}")
        print(traceback.format_exc())



                