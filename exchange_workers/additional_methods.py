from exchange_workers.kucoin import KuCoin
from exchange_workers.okx import OKX
from exchange_workers.bybit import BB
from exchange_workers.binance import BN
from exchange_workers.bitget import BG
from exchange_workers.bitmart import BM
from exchange_workers.bingx import BX
from exchange_workers.blofin.blofin import BF
from exchange_workers.phemex.phemex import PM
from exchange_workers.xt import XT
import shared_vars as sv
import traceback
import json

def save_data_to_file(exchanges, filename):
    with open(filename, 'w') as f:
        json.dump(exchanges, f)

def load_data_from_file(filename):
    with open(filename, 'r') as f:
        exchanges = json.load(f)
    return exchanges

async def get_coin_sets():
    try:
        sv.manager_instance = 1
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
        report = {}
        for key, val in exchanges.items():
            sv.settings_gl.exchange = key
            sv.settings_gl.API_KEY = f'{sv.settings_gl.exchange}API_{sv.manager_instance}'
            sv.settings_gl.SECRET_KEY = f'{sv.settings_gl.exchange}SECRET_{sv.manager_instance}'
            val.init(sv.settings_gl)
            res, contracts = val.is_contract_exist('BTCUSDT')
            print(key, contracts)
            report[key] = contracts

        save_data_to_file(report, 'contracts.json')
    except Exception as e:
        print(e)
        print(traceback.format_exc())

def missing_contracts(exchanges, contracts):
    report = {}
    for exchange, exchange_contracts in exchanges.items():
        missing = [contract for contract in contracts if contract not in exchange_contracts]
        report[exchange] = missing
    return report

def common_contracts(exchanges, min_exchanges):
    contract_counts = {}
    for exchange_contracts in exchanges.values():
        for contract in exchange_contracts:
            if contract not in contract_counts:
                contract_counts[contract] = 0
            contract_counts[contract] += 1
    common = [contract for contract, count in contract_counts.items() if count >= min_exchanges]
    return common

def contract_exchanges(exchanges, contract):
    included_exchanges = [exchange for exchange, contracts in exchanges.items() if contract in contracts]
    return len(included_exchanges), included_exchanges

async def work(num):
    exchanges = load_data_from_file('contracts.json')
    # missing = missing_contracts(exchanges, sv.best_set)
    common = common_contracts(exchanges, num)
    # print(missing)
    return common, exchanges['BN']

def recalculate_budget_multiplier(amount, num_exchanges, coin):
    total_budget = amount*num_exchanges
    contracts = load_data_from_file('contracts.json')
    available_exchanges, ex = contract_exchanges(contracts, coin)
    available_exchanges = 7 if available_exchanges < 7 else available_exchanges
    print(f'Contract {coin} exist in {available_exchanges} exchanges. Amount will be recalculate.')
    budget =  total_budget / available_exchanges
    koff = budget/amount
    return koff