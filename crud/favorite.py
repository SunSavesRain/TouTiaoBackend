from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete,func
from models.news import News
from models.favorite import Favorite

# 检查指定用户是否收藏了指定的新闻
async def check_user_favorite_status(db: AsyncSession, user_id: int, news_id: int):
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    favorite = result.scalar_one_or_none()
    return favorite is not None

# 添加新闻收藏
async def add_user_favorite(db: AsyncSession, user_id: int, news_id: int):
    # 检查是否已经收藏过
    if await check_user_favorite_status(db, user_id, news_id):
        raise HTTPException(status_code=400, detail="新闻已收藏")
    new_favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)
    return new_favorite

#取消新闻收藏
async def remove_user_favorite(db: AsyncSession, user_id: int, news_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail="新闻已未收藏")
    return True

#获取用户新闻收藏列表的总量
async def get_user_favorite_count(db: AsyncSession, user_id: int):
    stmt = select(func.count()).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar()

#获取新闻收藏列表
async def get_user_favorite_list(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    #联合查询，select(主体类,字段(别名)).join(关联类, 关联条件)，返回的内容只有主体类的内容
    stmt = (select(News, Favorite.id.label("favorite_id"),Favorite.created_at.label("favorite_time")
                  ).join(Favorite, News.id == Favorite.news_id
                  ).where(Favorite.user_id == user_id
                  ).order_by(Favorite.created_at.desc()
                  ).offset(skip).limit(limit))
    result = await db.execute(stmt)
    favorite_news = result.all()
    return favorite_news

#清空收藏列表
async def clear_user_favorite(db: AsyncSession, user_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    await db.execute(stmt)
    await db.commit()
    return True
