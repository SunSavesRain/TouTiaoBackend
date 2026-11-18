from fastapi import HTTPException, Query
from sqlalchemy import select, func, or_,and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.comment import Comment
from models.users import User
from models.news import News

#根据关键词查询评论
async def get_admin_comments(db: AsyncSession,page: int = Query(1, title="页码"),
                             page_size: int = Query(10, alias="pageSize", title="每页数量")
                             ,keyword: str | None = None):
    offset = (page - 1) * page_size
    stmt = (select(Comment.id,Comment.user_id, Comment.content, Comment.created_at,
                   Comment.news_id,User.username, User.nickname,News.title.label("news_title"))
            .join(User, Comment.user_id == User.id).join(News, Comment.news_id == News.id))
    count_stmt = (
        select(func.count(Comment.id))
        .join(User, Comment.user_id == User.id)
        .join(News, Comment.news_id == News.id)
    )
    #过滤空格
    if keyword:
        keyword = keyword.strip()
    if keyword:
        keywords = keyword.strip().split()
        conditions = []
        for word in keywords:
            keyword_pattern = f"%{word}%"
            conditions.append(or_(Comment.content.like(keyword_pattern), User.username.like(keyword_pattern),
                              User.nickname.like(keyword_pattern), News.title.like(keyword_pattern)))
        condition = and_(*conditions)
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    stmt = stmt.order_by(Comment.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    comments = result.mappings().all()
    total = await db.execute(count_stmt)
    total_count = total.scalar_one()
    return comments, total_count

#删除评论
async def delete_admin_comment(db: AsyncSession,comment_id: int):
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    await db.delete(comment)
    await db.commit()
    return True

