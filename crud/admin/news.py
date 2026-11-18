from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func,or_, and_
from cache.news_cache import delete_cache_news_detail, delete_cache_news_list, delete_cache_news_related
from enums.news import NewsStatus
from models.news import Category, News
from schemas.admin.news import AdminNewsCreate, AdminNewsUpdate
from fastapi import HTTPException
from datetime import datetime

#搜索新闻
async def get_admin_news_list(db: AsyncSession,keyword: str | None = None,page: int = 1,page_size: int = 8,
                      category_id: int | None = None,status: NewsStatus | None = None):
    conditions = []
    if keyword:
        keywords = keyword.strip().split()
        for word in keywords:
            keyword_pattern = f"%{word}%"
            conditions.append(or_(News.title.like(keyword_pattern), News.description.like(keyword_pattern),
                                  News.content.like(keyword_pattern),News.author.like(keyword_pattern)))
    if category_id is not None:
        conditions.append(News.category_id == category_id)
    if status is not None:
        conditions.append(News.status == status)
    offset = (page - 1) * page_size
    stmt = (select(News.id, News.title, News.category_id, Category.name.label("category"),
                   News.author, News.image, News.views, News.status, News.publish_time).
            join(Category, News.category_id == Category.id).
            order_by(News.id.desc()).limit(page_size).offset(offset))
    count_stmt = select(func.count(News.id)).join(Category, News.category_id == Category.id)
    if conditions:
        condition = and_(*conditions)
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    result = await db.execute(stmt)
    news_list = result.mappings().all()
    count_result = await db.execute(count_stmt)
    return news_list, count_result.scalar_one()

"""
获取指定新闻的详细信息
"""
async def get_admin_news_by_id(db :AsyncSession,news_id: int):
    stmt = (select(News.id,News.title,News.category_id,Category.name.label("category"),
            News.author,News.description,News.content,News.image,News.views,News.status,
            News.publish_time).join(Category, News.category_id == Category.id).where(News.id == news_id))
    result = await db.execute(stmt)
    news = result.mappings().one_or_none()
    if news:
        return news
    else:
        raise HTTPException(status_code=404, detail="新闻不存在")

#新增新闻
async def add_admin_news(db: AsyncSession,news_data: AdminNewsCreate):
    stmt = select(Category).where(Category.id == news_data.category_id)
    result = await db.execute(stmt)
    category = result.scalars().one_or_none()
    if category is None:
        raise HTTPException(status_code=400, detail="新增新闻的分类不存在")
    publish_time = None
    if news_data.status == NewsStatus.published:
        publish_time = datetime.now()
    news = News(title=news_data.title,category_id=news_data.category_id,author=news_data.author,
        description=news_data.description,content=news_data.content,image=news_data.image,
        status=news_data.status,publish_time=publish_time,views=0)
    db.add(news)
    await db.commit()
    await db.refresh(news)
    await delete_cache_news_list()
    return news,category.name


#更新新闻
async def update_admin_news(db: AsyncSession,news_id: int,news_data: AdminNewsUpdate):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalars().one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="更新新闻的新闻不存在")
    old_image = news.image
    category = None
    if news_data.category_id is not None:
        stmt = select(Category).where(Category.id == news_data.category_id)
        result = await db.execute(stmt)
        category = result.scalars().one_or_none()
        if category is None:
            raise HTTPException(status_code=400, detail="更新新闻的分类不存在")
    if news_data.status == NewsStatus.published and news.status != NewsStatus.published:
        news.publish_time = datetime.now()
    update_data = news_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(news, key, value)
    await db.commit()
    await db.refresh(news)
    if category is None:
        stmt = select(Category).where(Category.id == news.category_id)
        result = await db.execute(stmt)
        category = result.scalar_one()
    await delete_cache_news_detail(news_id)
    await delete_cache_news_list()
    return news, category.name, old_image

#删除新闻
async def delete_admin_news(db: AsyncSession,news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalars().one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="删除新闻的新闻不存在")
    old_image = news.image
    await db.delete(news)
    await db.commit()
    await delete_cache_news_detail(news_id)
    await delete_cache_news_list()
    await delete_cache_news_related()
    return old_image

