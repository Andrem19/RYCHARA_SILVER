from helpers.redisdb import RD

def seed_db():
    worker_settings = {
        'max_amount': 25,
        'border_saldo': '03.12.23',
        'message_timer': 80,
        'collector_bot': 'COLLECTOR'
    }
    RD.write_dict('settings:worker', worker_settings)
