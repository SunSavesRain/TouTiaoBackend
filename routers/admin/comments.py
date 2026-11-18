from fastapi import APIRouter, Depends, HTTPException,Query
from crud.admin.comments import get_admin_comments, delete_admin_comment
from schemas.admin.comments import AdminCommentResponse, AdminCommentListResponse
from utils.auth import get_current_admin
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from utils.response import success_response

router = APIRouter(
    prefix="/api/admin/comments",
    tags=["后台-评论管理"],
    dependencies=[Depends(get_current_admin)]
)

#根据关键词查询评论
@router.get("")
async def get_admin_comments_api(db: AsyncSession = Depends(get_database), page: int = 1, page_size: int = 10,
                            keyword: str | None = Query(default=None)):
    comments, total_count = await get_admin_comments(db, page, page_size, keyword)
    comment_list = [AdminCommentResponse.model_validate(item) for item in comments]
    data = AdminCommentListResponse(list = comment_list,total=total_count)
    return success_response(data=data, message="获取评论列表成功")

#删除评论
@router.delete("/{comment_id}")
async def delete_admin_comment_api(comment_id: int, db: AsyncSession = Depends(get_database)):
    result = await delete_admin_comment(db, comment_id)
    if result:
        return success_response(message="删除评论成功")
    else:
        raise HTTPException(status_code=404, detail="评论不存在")


