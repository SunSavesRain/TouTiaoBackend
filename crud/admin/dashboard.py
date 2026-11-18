from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from models.news import News, Category
from models.users import User
from models.comment import Comment
from models.visit_stats import DailyVisitStats
from datetime import date, timedelta

# 获取仪表盘统计信息：总新闻数、总用户数、总评论数、总浏览数
async def get_dashboard_stats(db: AsyncSession):
    result = await db.execute(select(func.count(News.id)))
    total_news = result.scalar_one()
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar_one()
    result = await db.execute(select(func.count(Comment.id)))
    total_comments = result.scalar_one()
    #coalesce的作用是若新闻表为空不使用None而是替换为0
    result = await db.execute(select(func.coalesce(func.sum(News.views), 0)))
    total_views = result.scalar_one()
    return {
        "news": total_news,
        "users": total_users,
        "comments": total_comments,
        "views": total_views
    }

# 获取分类分布情况
async def get_category_distribution(db: AsyncSession):
    stmt=(
        select(Category.name, func.count(News.id).label("value")).
        outerjoin(News, Category.id == News.category_id).
        group_by(Category.name, Category.id).
        order_by(Category.sort_order.asc()))
    result = await db.execute(stmt)
    return result.mappings().all()

#获取热门新闻数据
async def get_hot_news(db: AsyncSession,limit: int = 10):
    stmt = (select(News.id, News.title, News.views,
            Category.name.label("category"),
            func.count(Comment.id).label("comments")).
            join(Category, News.category_id == Category.id).
            outerjoin(Comment, News.id == Comment.news_id).
            group_by(News.id, News.title, News.views, Category.name)
            .order_by(News.views.desc(), News.id.desc()).limit(limit))
    result = await db.execute(stmt)
    return result.mappings().all()

#获取近期的新闻浏览情况
async def get_visit_trend(db: AsyncSession, limit: int = 7):
    today = date.today()
    start_date = today - timedelta(days=limit-1)
    stmt = (
        select(DailyVisitStats.stat_date,DailyVisitStats.views)
        .where(DailyVisitStats.stat_date >= start_date,DailyVisitStats.stat_date <= today)
        .order_by(DailyVisitStats.stat_date.asc()))
    result = await db.execute(stmt)
    stats = result.mappings().all()
    stats_dict = {item["stat_date"]: item["views"]for item in stats}
    data = []
    for i in range(limit):
        current_date = start_date + timedelta(days=i)
        data.append({
            "date": current_date.strftime("%m-%d"),
            "views": stats_dict.get(current_date, 0)
        })
    return data
