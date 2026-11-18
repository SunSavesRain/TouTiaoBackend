from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from enums.user import UserRole
from models.comment import Comment
from models.users import User
from models.news import News
from schemas.comments import CommentCreate


#查询指定新闻下的评论
async def get_comments(db: AsyncSession, news_id: int, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    stmt = (select(Comment.id,Comment.user_id, Comment.content, Comment.created_at,
                   User.username, User.nickname,User.avatar)
            .join(User, Comment.user_id == User.id)
            .where(Comment.news_id == news_id).order_by(Comment.created_at.desc())
            .offset(offset).limit(page_size))
    count_stmt = select(func.count(Comment.id)).where(Comment.news_id == news_id)
    result = await db.execute(stmt)
    comments = result.mappings().all()
    total = await db.execute(count_stmt)
    total_count = total.scalar_one()
    return comments, total_count

#删除评论
async def delete_comment(db: AsyncSession,comment_id: int,user: User):
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    if comment.user_id != user.id and user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="无权限删除评论")
    await db.delete(comment)
    await db.commit()
    return True

#添加评论
async def add_comment(db: AsyncSession, user_id: int,comment_data: CommentCreate):
    stmt = select(News).where(News.id == comment_data.news_id)
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")
    comment = Comment(user_id=user_id, news_id=comment_data.news_id, content=comment_data.content)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment
