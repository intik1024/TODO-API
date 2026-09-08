import redis
import json
from typing import Optional,Any,List

class RedisClient:
    def __init__(self,host='localhost',port=6379,db=0,decode_response=True):
        try:
            self.client=redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=decode_response
            )
            self.client.ping()
            self.enabled=True
            print('Redis подключен')
        except redis.ConnectionError:
            print('Redis не доступен работаем без кэширования')
            self.client=None
            self.enabled=False

    def get(self,key:str)-> Optional[Any]:
        if not self.enabled:
            return None
        try:
            data=self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print('Ошибка получения редис')
            return None

    def set(self,key:str,value:Any,expire:int=60):
        if not self.enabled:
            return
        try:
            self.client.setex(key,expire,json.dumps(value,default=str))
        except Exception as e:
            print(f'Ошибка сохранения Redis {e}')

    def delete(self,key:str):
        if not self.enabled:
            return
        try:
            self.client.delete(key)
        except Exception as e:
            print(f'Ошибка удаления Redis {e}')

    def clear_pattern(self,pattern:str):
        if not self.enabled:
            return
        try:
            keys=self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception as e:
            print(f'Ошибка чистки кеша {e}')
redis_client=RedisClient()



