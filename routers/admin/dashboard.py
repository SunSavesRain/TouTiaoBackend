from fastapi import APIRouter, Depends, HTTPException
from crud.admin.dashboard import get_dashboard_stats, get_visit_trend, get_category_distribution,get_hot_news
from schemas.admin.dashboard import CategoryDistributionItem, VisitTrendItem, HotNewsItem, DashboardStats, \
    DashboardResponse
from utils.auth import get_current_admin
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from utils.response import success_response

router = APIRouter(
    prefix="/api/admin/dashboard",
    tags=["后台-看板"],
    dependencies=[Depends(get_current_admin)]
)

# 获取看板数据
@router.get("")
async def get_dashboard_data_api(db: AsyncSession = Depends(get_database)):
    stats = await get_dashboard_stats(db)
    stats = DashboardStats.model_validate(stats)
    visit_trend = await get_visit_trend(db,7)
    category_distribution = await get_category_distribution(db)
    hot_news = await get_hot_news(db, 10)
    category_distribution_list = [CategoryDistributionItem.model_validate(item) for item in category_distribution]
    visit_trend_list = [VisitTrendItem.model_validate(item) for item in visit_trend]
    hot_news_list = [HotNewsItem.model_validate(item) for item in hot_news]
    data = DashboardResponse(stats=stats, visit_trend=visit_trend_list, category_distribution=category_distribution_list, hot_news=hot_news_list)
    return success_response(data=data, message="获取看板数据成功")


