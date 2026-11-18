from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, Update
from models.news import News
from models.history import History

# 获取指定用户的指定新闻的浏览历史
async def get_user_history(db: AsyncSession, user_id: int,news_id: int):
    stmt=select(History).where(History.user_id == user_id,History.news_id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# 添加用户新闻浏览历史
async def add_user_history(db: AsyncSession, user_id: int, news_id: int):
    history = await get_user_history(db,user_id,news_id)
    if history:
        history.view_time = datetime.now()
    else:
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

#获取指定用户的浏览历史的总数
async def get_user_history_count(db: AsyncSession, user_id: int):
    stmt=select(func.count()).where(History.user_id == user_id)
    result = await db.execute(stmt)
    history_count = result.scalar_one_or_none()
    if history_count is None:
        raise HTTPException(status_code=500, detail="获取用户新闻浏览历史列表总量失败")
    return history_count

#获取浏览历史列表
async def get_user_history_list(db: AsyncSession, user_id: int,skip: int = 0, limit: int = 10):
    stmt=select(News,History.view_time).join(History,History.news_id == News.id).where(History.user_id == user_id).order_by(History.view_time.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.all()

#删除指定用户的指定新闻的浏览历史
async def delete_user_history(db: AsyncSession,history_id: int):
    stmt=delete(History).where(History.id == history_id)
    await db.execute(stmt)
    await db.commit()
    return True

#清空指定用户的浏览历史
async def clear_user_history(db: AsyncSession, user_id: int):
    stmt=delete(History).where(History.user_id == user_id)
    await db.execute(stmt)
    await db.commit()
    return True

