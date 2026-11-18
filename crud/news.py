from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update,or_, and_
from cache.news_cache import get_cache_categories, set_cache_categories, get_cache_news_list, set_cache_news_list, \
    get_cache_news_detail, set_cache_news_detail, get_cache_news_related, set_cache_news_related
from enums.news import NewsStatus
from models.news import Category, News
from schemas.news import NewsItemAll
from fastapi import HTTPException
from models.visit_stats import DailyVisitStats
from datetime import date

"""
获取新闻分类列表
"""
async def get_categories(db :AsyncSession,skip: int = 0, limit: int = 100):
    cached_categories = await get_cache_categories()
    if cached_categories:
        return [Category(**item) for item in cached_categories]
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    if categories:
        await set_cache_categories(jsonable_encoder(categories))
    return categories
"""
获取指定分类下的新闻列表
"""
async def get_news_list(db :AsyncSession,category_id: int,skip: int = 0, limit: int = 10):
    cached_news = await get_cache_news_list(category_id,skip//limit+1,limit)
    if cached_news:
        return [News(**item) for item in cached_news]
    stmt = select(News).where(News.category_id == category_id,News.status == NewsStatus.published).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    if news_list:
        news_data = [NewsItemAll.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
        await set_cache_news_list(category_id,skip//limit+1,limit,news_data)
    return news_list
"""
获取指定分类下的新闻总数
"""
async def get_news_count_by_category(db :AsyncSession,category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id,News.status == NewsStatus.published)
    result = await db.execute(stmt)
    return result.scalar_one()
"""
增加新闻浏览量，返回最新的浏览量
"""
async def increment_news_views(db :AsyncSession,news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    if result.rowcount == 0:
        await db.rollback()
        return None
    stmt = select(News.views).where(News.id == news_id)
    result = await db.execute(stmt)
    views = result.scalar_one()
    await db.commit()
    return views
"""
获取相关新闻，排除当前新闻，根据分类判断相关，按发布时间和浏览量降序排序
"""
async def get_related_news(db: AsyncSession,news_id: int,category_id: int,limit: int = 5):
    cache_news = await get_cache_news_related(news_id,category_id,limit)
    if cache_news:
        return [News(**item) for item in cache_news]
    stmt = select(News).where(News.category_id == category_id,
                              News.id != news_id,News.status == NewsStatus.published).order_by(
                              News.publish_time.desc(),News.views.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    related_news_list = result.scalars().all()
    if related_news_list:
        await set_cache_news_related(news_id,category_id,jsonable_encoder(related_news_list),limit)
    return related_news_list

#获取新闻总数
async def get_news_total(db: AsyncSession):
    stmt = select(func.count(News.id)).where(News.status == NewsStatus.published)
    result = await db.execute(stmt)
    return result.scalar_one()

#按浏览量获取新闻
async def get_hot_news(db: AsyncSession,limit):
    stmt = select(News).where(News.status == NewsStatus.published).order_by(News.views.desc(), News.id.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

#搜索新闻
async def search_news(db: AsyncSession,keyword: str,page: int = 1,page_size: int = 20):
    keywords = keyword.strip().split()
    conditions = []
    for word in keywords:
        keyword_pattern = f"%{word}%"
        #or()满足条件中的一个，然后把针对每个关键词的or放入列表
        conditions.append(or_(News.title.like(keyword_pattern), News.description.like(keyword_pattern),
                              News.content.like(keyword_pattern),News.author.like(keyword_pattern)))
    #把所有的or展开然后用and组合,每个关键词都要在内容标题描述的其一出现
    condition = and_(*conditions)
    condition = and_(condition, News.status == NewsStatus.published)
    offset = (page - 1) * page_size
    stmt = select(News).where(condition).order_by(News.publish_time.desc(), News.id.desc()).limit(page_size).offset(offset)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    count_stmt = select(func.count(News.id)).where(condition)
    count_result = await db.execute(count_stmt)
    return news_list, count_result.scalar_one()

#增加每日访问量
async def increment_daily_visit_stats(db: AsyncSession):
    today = date.today()
    stmt = select(DailyVisitStats).where(DailyVisitStats.stat_date == today)
    result = await db.execute(stmt)
    stats = result.scalar_one_or_none()
    if stats:
        stats.views += 1
    else:
        stats = DailyVisitStats(stat_date=today, views=1)
        db.add(stats)
    await db.commit()
    return stats.views

"""
获取指定新闻的详细信息
"""
async def get_news_by_id(db :AsyncSession,news_id: int):
    cache_news = await get_cache_news_detail(news_id)
    if cache_news:
        new_data = News(**cache_news)
    else:
        stmt = select(News).where(News.id == news_id,News.status == NewsStatus.published)
        result = await db.execute(stmt)
        news = result.scalar_one_or_none()
        new_data = news
    if new_data:
        views = await increment_news_views(db, news_id)
        if views is not None:
            new_data.views = views
            await set_cache_news_detail(news_id, jsonable_encoder(new_data))
            await increment_daily_visit_stats(db)
            return new_data
        else:
            raise HTTPException(status_code=404, detail="增加浏览量的新闻不存在")
    else:
        raise HTTPException(status_code=404, detail="新闻不存在")
