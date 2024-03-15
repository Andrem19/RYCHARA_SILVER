# from models.settings import Settings
# from decouple import config
# from exchange_workers.bt_core import FutureClient
# import threading

# class BT:

#     client = None
#     init_lock = threading.Lock()

#     @staticmethod
#     def init(settings: Settings):
#         # Check if the variables are already set
#         if BT.client is not None:
#                 return
        
#         # Acquire the lock to ensure only one thread initializes the variables
#         with BT.init_lock:
#             # Check again after acquiring the lock in case another thread has already initialized the variables
#             if BT.client is not None:
#                 return
#             api_key = config(settings.API_KEY)
#             secret_key = config(settings.SECRET_KEY)

#             BT.client = FutureClient(api_key=api_key, api_secret=secret_key)

#     @staticmethod
#     def get_last_price(coin: str):
#         c = f'{coin[:-4]}-{coin[-4:]}'
#         params = {
#             'contractName': f'E-{c}'
#         }
#         last_price = BT.client.get_ticker(**params)
#         return last_price['last']
    
#     @staticmethod
#     def get_balance() -> float:
#         acc = BT.client.get_account()
#         if 'account' in acc:
#             for account in acc['account']:
#                 if account['marginCoin'] == 'USDT':
#                     return account['accountNormal']
#         else:
#             return 0
        
#     @staticmethod
#     def get_position(coin: str, signal: int):
#         side = 'BUY' if signal == 1 else 'SELL'
#         c = f'{coin[:-4]}-{coin[-4:]}'

#         acc = BT.client.get_account()
#         if 'account' in acc:
#             for account in acc['account']:
#                 if account['marginCoin'] == 'USDT':
#                     if len(account['positionVos']) > 0:
#                         for position in account['positionVos']:
#                             if position['contractName'] == f'E-{c}':
#                                 if len(position['positions']) > 0:
#                                     for pos in position['positions']:
#                                         if pos['side'] == side:
#                                             return pos
#         return None


#     @staticmethod
#     def get_contract_info(coin: str):
#         c = f'{coin[:-4]}-{coin[-4:]}'
#         contracts = BT.client.get_contracts()
#         for contract in contracts:
#             if contract['symbol'] == f'E-{c}':
#                 return contract

#     @staticmethod
#     def is_contrct_exist(coin: str):
#         contract_list = []
#         contracts = BT.client.get_contracts()
#         for contract in contracts:
#             parts = contract['symbol'].split('-')
#             symb = f'{parts[1]}{parts[2]}'
#             contract_list.append(symb)
#         if coin in contract_list:
#             return True, contract_list
#         return False, contract_list


#     @staticmethod
#     def cancel_all_orders(coin: str) -> str:
#         c = f'{coin[:-4]}-{coin[-4:]}'
#         try:
#             params = {
#             'contractName': f'E-{c}',
#             }
#             BT.client.cancel_order(**params)
            
#         except Exception as e:
#             print(f'Error: {e}')

#     @staticmethod
#     def get_history_trades(coin: str):
#         c = f'{coin[:-4]}-{coin[-4:]}'
#         # [{'amount': 19.8272, 'side': 'SELL', 'fee': '0.01387904', 'isMaker': False, 'isBuyer': False, 'bidId': 1991727621103995900, 'bidUserId': 10008, 'price': 0.6196, 'qty': 32, 'askId': 1991725817217681456, 'contractName': 'E-XRP-USDT', 'time': 1704046945000, 'tradeId': 34794597, 'askUserId': 293603}, {'amount': 0.6197, 'side': 'BUY', 'fee': '0.00043379', 'isMaker': False, 'isBuyer': True, 'bidId': 1991727569564373973, 'bidUserId': 293603, 'price': 0.6197, 'qty': 1, 'askId': 1991727552384488553, 'contractName': 'E-XRP-USDT', 'time': 1704046893000, 'tradeId': 34794581, 'askUserId': 10008}, {'amount': 19.2107, 'side': 'BUY', 'fee': '0.01344749', 'isMaker': False, 'isBuyer': True, 'bidId': 1991727569564373973, 'bidUserId': 293603, 'price': 0.6197, 'qty': 31, 'askId': 1991725782857947130, 'contractName': 'E-XRP-USDT', 'time': 1704046892000, 'tradeId': 34794580, 'askUserId': 293851}, {'amount': 4.3253, 'side': 'SELL', 'fee': '0.00302771', 'isMaker': False, 'isBuyer': False, 'bidId': 1991711592286013750, 'bidUserId': 10008, 'price': 0.6179, 'qty': 7, 'askId': 1991709822759454161, 'contractName': 'E-XRP-USDT', 'time': 1703991053000, 'tradeId': 34777285, 'askUserId': 293603}, {'amount': 15.4475, 'side': 'SELL', 'fee': '0.01081325', 'isMaker': False, 'isBuyer': False, 'bidId': 1991709547881568865, 'bidUserId': 200694, 'price': 0.6179, 'qty': 25, 'askId': 1991709822759454161, 'contractName': 'E-XRP-USDT', 'time': 1703991053000, 'tradeId': 34777284, 'askUserId': 293603}, {'amount': 19.7856, 'side': 'BUY', 'fee': '0.01384992', 'isMaker': False, 'isBuyer': True, 'bidId': 1991711557926277400, 'bidUserId': 293603, 'price': 0.6183, 'qty': 32, 'askId': 1991709788399716716, 'contractName': 'E-XRP-USDT', 'time': 1703990956000, 'tradeId': 34777252, 'askUserId': 10008}]
#         params = {
#             'contractName': f'E-{c}',
#         }
#         position = BT.client.get_my_trades(**params)
#         print(position)
        
#     @staticmethod
#     def open_order(coin: str, sd: str, amount_usdt: int, reduceOnly: bool, coin_amount = 0) -> str:
#         try:
#             contract = BT.get_contract_info(coin)
#             minTradeNum = contract['minOrderVolume']
#             sizeMultiplier = contract['multiplier']
#             precision = contract['pricePrecision']

#             side = 'BUY' if sd == 'Buy' else 'SELL'
#             c = f'{coin[:-4]}-{coin[-4:]}'
#             last_price = BT.get_last_price(coin)
#             pr = 0
#             if side == 'BUY':
#                 pr = last_price * (1+0.0001)
#             else:
#                 pr = last_price * (1-0.0001)

#             size = amount_usdt / last_price
#             open = 'OPEN'
#             if reduceOnly == True:
#                 side = 'SELL' if sd == 'Buy' else 'BUY'
#                 open = 'CLOSE'

#             size = size//sizeMultiplier

#             if size < minTradeNum:
#                 size = minTradeNum
#             ord_type = 'MARKET'
#             params = {
#                 'contractName': f'E-{c}',
#                 'side': side,
#                 'type': 'MARKET',
#                 'positionType': 1,
#                 'open': open,
#                 'volume': size,
#                 'price': round(pr, precision),
#             }
#             print(params)
#             res = BT.client.create_order(**params)
#             print(res)
#             return res['orderId'], pr
#             # return order_id, pr
#         except Exception as e:
#             print(f'Error: {e}')
#             return 0, 0
    
#     @staticmethod
#     def open_SL(coin: str, sd: str, amount_lot: str, open_price: float, SL_perc: float):
#         try:
#             contract = BT.get_contract_info(coin)
#             precision = contract['pricePrecision']
#             side = 'SELL' if sd == 'Buy' else 'BUY'
#             c = f'{coin[:-4]}-{coin[-4:]}'
#             price = 0
#             if side == 'BUY':
#                 price = open_price * (1+SL_perc)
#             elif side == 'SELL':
#                 price = open_price * (1-SL_perc)
#             size = amount_lot
            
#             params = {
#                 'contractName': f'E-{c}',
#                 'side': 'SELL',
#                 'type': 'LIMIT',
#                 'positionType': 1,
#                 'open': 'CLOSE',
#                 'volume': round(int(size), 0),
#                 # 'amount': 1,
#                 'price': round(price, precision),
#             }
#             print(params)
#             res = BT.client.create_order(**params)
#             print(res)
#             return res['orderId']
#         except Exception as e:
#             print(f'Error: {e}')
#             return 0, 0