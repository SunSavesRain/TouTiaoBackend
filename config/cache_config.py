import os
import json
from typing import Any
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

#封装：读取字符串
async def get_cache_str(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取字符串类型缓存失败：{e}")
        return None

#封装：读取列表或者字典
async def get_cache_json(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取列表或字典类型缓存失败：{e}")
        return None

#封装：设置缓存
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)#将字典或列表转成字符串，同时保留中文不转义
        await redis_client.set(key, value, expire)
        return True
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return False

#封装：删除缓存
async def delete_cache(key: str):
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        print(f"删除缓存失败：{e}")
        return False
