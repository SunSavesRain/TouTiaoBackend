from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud.comments import get_comments, delete_comment, add_comment
from schemas.comments import CommentItem, CommentListResponse, CommentCreate
from utils.response import success_response
from utils.auth import get_current_user
from models.users import User

router = APIRouter(
    prefix="/api/comments",
    tags=["用户评论"])

# 获取用户评论
@router.get("")
async def get_comments_api(
    db: AsyncSession = Depends(get_database),news_id: int = Query(..., alias="newsId"),
    page: int = Query(1, title="页码"),
    page_size: int = Query(10, alias="pageSize", title="每页数量")):
    comments, total_count = await get_comments(db, news_id, page, page_size)
    comments_list = [CommentItem.model_validate(item) for item in comments]
    has_more = total_count > page * page_size
    data = CommentListResponse(total=total_count, list=comments_list, has_more=has_more)
    return success_response(data=data, message="获取评论列表成功")

# 删除评论
@router.delete("/{comment_id}")
async def delete_comment_api(comment_id: int,db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)):
    await delete_comment(db, comment_id, user)
    return success_response(message="删除评论成功")

# 添加评论
@router.post("")
async def add_comment_api(comment_data: CommentCreate,db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)):
    comment = await add_comment(db, user.id, comment_data)
    data = CommentItem(
        id=comment.id,
        user_id=comment.user_id,
        username=user.username,
        nickname=user.nickname,
        avatar=user.avatar,
        content=comment.content,
        created_at=comment.created_at
    )
    return success_response(data=data, message="添加评论成功")



