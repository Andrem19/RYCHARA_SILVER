import json

class Settings:
    def __init__(self):
        self.exchange: str = 'KC'
        self.name: str = ''
        self.API_KEY: str = 'KCAPI_1'
        self.SECRET_KEY: str = 'KCSECRET_1'
        self.telegram_token: str = ''
        self.coin: str = 'BTCUSDT'
        self.timeframe: int = 1
        self.stop_loss: float = 0.005
        self.take_profit: float = 0.005
        self.message_timer: int = 40
        self.target_len: int = 3
        self.my_uid: str = ''
        self.collector_bot: str = 'COLLECTOR'
        self.amount_usdt: float = 20
        self.max_amount: int = 100
        self.type_of_signal: int = 1
        self.border_saldo: str = '03.12.23'
        self.pause: int = 5

    def get_types_dict(self):
        types_dict = {attr: type(getattr(self, attr)) for attr in vars(self)}
        return types_dict
    
    def to_json(self):
            with open(f"settings/settings_UNIVERSAL.json", "w") as file:
                json.dump(self.__dict__, file)
        
    def from_json(self):
        with open(f"settings/settings_UNIVERSAL.json", "r") as file:
            data = json.load(file)
            for key, value in data.items():
                setattr(self, key, value)
                
    def from_dict(self, set_dict: dict):
        types_dict = self.get_types_dict()
        for key, value in set_dict.items():
            if key in types_dict:
                expected_type = types_dict[key]
                if not isinstance(value, expected_type):
                    value = expected_type(value)
            setattr(self, key, value)

# set = Settings()
# set.to_json()