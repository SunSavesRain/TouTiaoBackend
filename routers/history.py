from fastapi import APIRouter, Depends,HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud.history import add_user_history, get_user_history_list, get_user_history_count, delete_user_history, \
    clear_user_history
from schemas.history import HistoryAddRequest, HistoryAddResponse, HistoryListItem, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response
from models.users import User

router = APIRouter(prefix="/api/history", tags=["history"])

#添加新闻浏览历史api
@router.post("/add")
async def add_history_api(
    data: HistoryAddRequest,
    db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)):
    result = await add_user_history(db, user.id, data.news_id)
    if result:
        return success_response(message="添加历史记录成功",data=HistoryAddResponse.model_validate(result))
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="添加历史记录失败")

#获取新闻浏览历史列表api
@router.get("/list")
async def get_history_list_api(db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user),page: int = Query(1,ge=1),page_size: int = Query(10,ge=1,le=100)):
    offset = (page - 1) * page_size
    row = await get_user_history_list(db, user.id, skip=offset, limit=page_size)
    history_list = [HistoryListItem(
        **news.__dict__,
        view_time=view_time
    ) for news,view_time in row]
    total = await get_user_history_count(db, user.id)
    has_more = total > offset + page_size
    data = HistoryListResponse(
        total=total,
        has_more=has_more,
        list=history_list
    )
    return success_response(message="获取历史记录列表成功",data=data)

#删除单条新闻浏览历史api
@router.delete("/delete/{history_id}")
async def delete_history_api(history_id: int,db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)):
    await delete_user_history(db,history_id)
    return success_response(message="删除历史记录成功")

#清空新闻浏览历史api
@router.delete("/clear")
async def clear_history_api(db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)):
    await clear_user_history(db, user.id)
    return success_response(message="清空历史记录成功")

