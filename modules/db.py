from redis import Redis
import os
from dotenv import load_dotenv

# ? init enviroment variables
load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_ID = os.getenv('DB_ID')


redis_store = Redis(DB_HOST,DB_PORT,DB_ID)

def set_key(key, value, expire=None, same_ttl=False):
    if isinstance(value, int):
        value = str(value)
    return redis_store.set(key, value, expire, xx=same_ttl)

def get_key(key):
    result = redis_store.get(key)
    if result:
        state = result.decode()
        try:
            return int(state)
        except ValueError:
            return state
    else:
        return result
    
def delete_key(id: int , key=None) -> bool:
    if not key:
        key = f"user:{id}:state"

    if redis_store.delete(key) == 1:
        return True
    else:
        return False

