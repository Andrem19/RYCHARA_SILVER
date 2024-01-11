import redis
from redis import Redis
from redis import StrictRedis
import threading
from decouple import config

class RD:
    _client: Redis = None
    _lock = threading.Lock()

    @staticmethod
    def initialize():
        if RD._client is not None:
            return

        with RD._lock:
            if RD._client is not None:
                return
            password = config("PASSWORD")
            try:
                RD._client = redis.Redis(host='localhost', port=6379, decode_responses=True, username='curuvar', password=password)
                # RD._client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            except redis.RedisError as e:
                print(f"Error with connection to Redis: {e}")
                raise
    

    @staticmethod
    def clear_database():
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            RD._client.flushall()
        except redis.RedisError as e:
            print(f"[clear_database] Error with clearing Redis database: {e}")
            raise e
        
    @staticmethod
    def write_dict(dict_key: str, dict_val: dict):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            RD._client.hset(dict_key, mapping=dict_val)
        except redis.RedisError as e:
            print(f"[write_dict] Error with writing to Redis: {e}")
    
    @staticmethod
    def rewrite_one_field(dict_key: str, field: str, val):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            RD._client.hset(dict_key, field, val)

        except redis.RedisError as e:
            print(f"[rewrite_one_field] Error with writing to Redis: {e}")

    @staticmethod
    def delete_one_field(dict_key: str, field: str):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            RD._client.hdel(dict_key, field)

        except redis.RedisError as e:
            print(f"[rewrite_one_field] Error with writing to Redis: {e}")
    
    @staticmethod
    def read_dict(dict_key: str) -> dict:
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            res_dict = RD._client.hgetall(dict_key)
            return res_dict
        except redis.RedisError as e:
            print(f"[read_dict] Error with writing to Redis: {e}")
    
    @staticmethod
    def read_dict_field(dict_key: str, field):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            value = RD._client.hget(dict_key, field)
            return value
        except redis.RedisError as e:
            print(f"[read_dict_field] Error with writing to Redis: {e}")

    @staticmethod
    def write_list(list_key: str, val: list):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")

        try:
            RD._client.delete(list_key)

            if len(val) > 0:
                for element in val:
                    RD._client.rpush(list_key, element)
        except redis.RedisError as e:
            print(f"[write_list] Error with writing to Redis: {e}")

    
    @staticmethod
    def add_val_to_list(list_key: str, val):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            RD._client.rpush(list_key, val)
        except redis.RedisError as e:
            print(f"[add_val_to_list] Error with writing to Redis: {e}")

    @staticmethod
    def return_list(list_key: str, last_element: bool = False):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            start = -1 if last_element else 0
            res_list = RD._client.lrange(list_key, start, -1)
            if last_element:
                return res_list[-1]
            else:
                return res_list
        except redis.RedisError as e:
            print(f"[return_list] Error with writing to Redis: {e}")
    
    @staticmethod
    def delete_pop_list(list_key: str):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            RD._client.rpop(list_key)
        except redis.RedisError as e:
            print(f"[delete_pop_list] Error with writing to Redis: {e}")
    
    @staticmethod
    def delete_key(key: str):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            RD._client.delete(key)
        except redis.RedisError as e:
            print(f"[delete_key] Error with writing to Redis: {e}")

    @staticmethod
    def write_val(key: str, val):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            RD._client.set(key, val)
        except redis.RedisError as e:
            print(f"[write_val] Error with writing to Redis: {e}")
    
    @staticmethod
    def get_val(key: str):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            val = RD._client.get(key)
            return val
        except redis.RedisError as e:
            print(f"[get_val] Error with writing to Redis: {e}")

    @staticmethod
    def load_all_key(key_pattern: str):
        if RD._client is None:
            raise Exception("Redis client not initialized. Call RedisDatabase.initialize() first.")
        
        try:
            coin_collection = []
            keys = RD._client.keys(f'{key_pattern}:*')
            for key in keys:
                data_type = RD._client.type(key)
                if data_type == 'string':
                    value = RD._client.get(key)
                elif data_type == 'list':
                    value = RD._client.lrange(key, 0, -1)
                elif data_type == 'hash':
                    value = RD._client.hgetall(key)
                else:
                    print(f"Unsupported data type: {data_type}")
                    continue
                coin_collection.append(value)
            return coin_collection
        except redis.RedisError as e:
            print(f"[load_all_key] Error with writing to Redis: {e}")
