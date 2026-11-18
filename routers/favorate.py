from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud.favorite import check_user_favorite_status, add_user_favorite, remove_user_favorite, get_user_favorite_count, \
    get_user_favorite_list, clear_user_favorite
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteAddResponse, FavoriteListResponse, \
    FavoriteNewsItem
from utils.auth import get_current_user
from utils.response import success_response
from models.users import User

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
#检查新闻是否被收藏api
async def check_favorite_status_api(db: AsyncSession = Depends(get_database), user: User = Depends(get_current_user), news_id: int = Query(...,alias="newsId")):
    result = await check_user_favorite_status(db, user.id, news_id)
    return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(isFavorite=result))

#添加新闻收藏api
@router.post("/add")
async def add_favorite_api(data: FavoriteAddRequest,db: AsyncSession = Depends(get_database), user: User = Depends(get_current_user)):
    result = await add_user_favorite(db, user.id, data.news_id)
    return success_response(message="添加收藏成功",data=FavoriteAddResponse.model_validate(result))

#取消新闻收藏api
@router.delete("/remove")
async def remove_favorite_api(db: AsyncSession = Depends(get_database), user: User = Depends(get_current_user), news_id: int = Query(...,alias="newsId")):
    await remove_user_favorite(db, user.id, news_id)
    return success_response(message="取消收藏成功")

#获取收藏列表api
@router.get("/list")
async def get_favorite_list_api(db: AsyncSession = Depends(get_database), user: User = Depends(get_current_user),
                                page: int = Query(1,ge=1),
                                page_size: int = Query(10,ge=1,le=100,alias="pageSize")):
    offset = (page - 1) * page_size
    total = await get_user_favorite_count(db, user.id)
    row = await get_user_favorite_list(db, user.id, skip=offset, limit=page_size)
    favorite_list = [FavoriteNewsItem(
        **news.__dict__,
        favorite_id=favorite_id,
        favorite_time=favorite_time
    ) for news,favorite_id,favorite_time in row]
    has_more = total > offset + page_size
    data = FavoriteListResponse(list=favorite_list, total=total, has_more=has_more)
    return success_response(message="获取收藏列表成功", data=data)

#清空收藏列表api
@router.delete("/clear")
async def clear_favorite_list_api(db: AsyncSession = Depends(get_database), user: User = Depends(get_current_user)):
    await clear_user_favorite(db, user.id)
    return success_response(message="清空收藏列表成功")


