from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from cache.news_cache import increment_hot_search, get_hot_search
from config.db_config import get_database
from crud.news import get_categories, get_news_list, get_news_count_by_category, get_news_by_id, increment_news_views, \
    get_related_news, get_hot_news, get_news_total, search_news
from schemas.news import NewsRelatedItemResponse, NewsDetailResponse, NewsListResponse, ConNewsListResponse
from utils.response import success_response

router = APIRouter(prefix="/api/news", tags=["news"])

"""
获取所有新闻分类api
"""
@router.get("/categories")
async def get_news_categories_api(skip: int = 0, limit: int = 100, db=Depends(get_database)):
    categories = await get_categories(db, skip=skip, limit=limit)
    if not categories:
        raise HTTPException(status_code=500, detail="获取新闻分类失败")
    return success_response(data=categories, message="获取新闻分类成功")

#获取热点新闻api
@router.get("/hot")
async def get_hot_news_api(limit: int = Query(default=20, ge=1, le=100),db: AsyncSession = Depends(get_database)):
    hot_news = await get_hot_news(db,limit)
    total = len(hot_news)
    total = limit if total > limit else total
    data = ConNewsListResponse(list = hot_news,total = total)
    return success_response(data=data, message="获取热点新闻成功")

"""
获取指定分类下的所有新闻api
"""
@router.get("/list")
async def get_news_list_api(category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(default=10,alias="pageSize",le=100),
        db : AsyncSession = Depends(get_database)):
    offset = (page - 1) * page_size
    news_list = await get_news_list(db, category_id, skip=offset, limit=page_size)
    if not news_list:
        raise HTTPException(status_code=500, detail="获取新闻列表失败")
    total = await get_news_count_by_category(db, category_id)
    if not total:
        raise HTTPException(status_code=500, detail="获取新闻总数失败")
    has_more = total > (offset + len(news_list))
    data = NewsListResponse(list = news_list, total = total, hasMore = has_more)
    return success_response(data=data, message="获取新闻列表成功")
"""
获取指定新闻详情api
"""
@router.get("/detail")
async def get_news_detail_api(news_id: int=Query(..., alias="id"), db: AsyncSession = Depends(get_database)):
    new=await get_news_by_id(db, news_id)
    if not new:
        raise HTTPException(status_code=404, detail="新闻不存在")
    related_news = await get_related_news(db, news_id, new.category_id)
    related_news = [NewsRelatedItemResponse.model_validate(item) for item in related_news]
    data = NewsDetailResponse.model_validate(new)
    data.related_news = related_news
    return success_response(data=data, message="获取新闻详情成功")

#获取相关新闻api
@router.get("/related")
async def get_related_news_api(news_id: int,category_id: int,limit: int = 5,db: AsyncSession = Depends(get_database)):
    related_news = await get_related_news(db, news_id, category_id,limit)
    related_news = [NewsRelatedItemResponse.model_validate(item) for item in related_news]
    return success_response(data=related_news, message="获取相关新闻成功")

#搜索新闻api
@router.get("/search")
async def search_news_api(keyword: str = Query(..., min_length=1), page: int = Query(default=1, ge=1),
                         page_size: int = Query(default=20, alias="pageSize", ge=1, le=100), db: AsyncSession = Depends(get_database)):
    keyword = " ".join(keyword.strip().split())
    if not keyword:
        return success_response(data=ConNewsListResponse(list=[], total=0), message="搜索成功")
    news_list, total = await search_news(db, keyword, page, page_size)
    if page == 1 and total > 0:
        await increment_hot_search(keyword)
    data = ConNewsListResponse(list = news_list, total = total)
    return success_response(data=data, message="获取新闻列表成功")

@router.get("/hot-search")
async def get_hot_search_api(limit: int = Query(default=10, ge=1, le=50)):
    hot_search = await get_hot_search(limit)
    return success_response(data=hot_search, message="获取热门搜索成功")


