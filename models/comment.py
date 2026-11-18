from datetime import datetime
from sqlalchemy import Integer, Text, DateTime, ForeignKey,Index, func
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from models.users import User
from models.news import News

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )

class Comment(Base):
    __tablename__ = "news_comments"
    __table_args__ = (
        Index("fk_comment_user_idx", "user_id"),
        Index("fk_comment_news_idx", "news_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="评论ID")
    user_id: Mapped[int] = mapped_column(INTEGER(unsigned=True), ForeignKey(User.id,ondelete="CASCADE"), comment="用户ID")
    news_id: Mapped[int] = mapped_column(INTEGER(unsigned=True), ForeignKey(News.id,ondelete="CASCADE"), comment="新闻ID")
    content: Mapped[str] = mapped_column(Text, comment="评论内容")

    def __repr__(self):
        return f"Comment(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, content={self.content})"

