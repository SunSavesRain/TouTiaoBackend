from config.cache_config import get_cache_json, set_cache, delete_cache
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models.users import UserToken

USERS_BY_TOKEN_PREFIX = "user_by_token"

async def set_cache_by_token(token: str,data: Dict[str,Any]):
    key = f"{USERS_BY_TOKEN_PREFIX}:{token}"
    result = await set_cache(key,data,7200)
    return result

async def get_cache_by_token(token: str):
    key = f"{USERS_BY_TOKEN_PREFIX}:{token}"
    result = await get_cache_json(key)
    return result

async def delete_cache_by_token(token: str):
    try:
        key = f"{USERS_BY_TOKEN_PREFIX}:{token}"
        await delete_cache(key)
        return True
    except Exception as e:
        print(f"删除用户缓存失败：{e}")
        return False

async def get_token_by_user_id(db: AsyncSession, user_id: int):
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()
    if token is None:
        raise HTTPException(status_code=404, detail="用户token不存在")
    return token.token

#根据用户id删除缓存
async def delete_cache_by_user_id(db: AsyncSession,user_id: int):
    token = await get_token_by_user_id(db,user_id)
    await delete_cache_by_token(token)
    return True
