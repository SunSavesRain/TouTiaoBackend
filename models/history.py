from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Text, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from models.users import User
from models.news import News

class Base(DeclarativeBase):
    view_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="访问时间"
    )

class History(Base):
    __tablename__ = "history"
    __table_args__ = (
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_news_idx", "news_id"),
        Index("idx_view_time", "view_time")
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="历史记录ID", autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id,ondelete="CASCADE"), nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id,ondelete="CASCADE"), nullable=False, comment="新闻ID")

    def __repr__(self):
        return f"History(id={self.id}, user_id={self.user_id}, news_id={self.news_id},view_time={self.view_time})"