from datetime import datetime
from sqlalchemy import DateTime, Integer,Index, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from models.users import User
from models.news import News #此类与新闻和用户类不继承同一Base，因此在设置外键时需要导入进行关联



class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

class Favorite(Base):
    __tablename__ = "favorite"
    __table_args__ = (
        Index("fk_favorite_user_idx", "user_id"),
        Index("fk_favorite_news_idx", "news_id"),
        Index("user_news_unique", "user_id", "news_id", unique=True)  # 建立联合唯一索引确保同一用户不能重复收藏
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="收藏ID", autoincrement=True)
    user_id: Mapped[int] = mapped_column(INTEGER(unsigned=True), ForeignKey(User.id,ondelete="CASCADE"), nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(INTEGER(unsigned=True), ForeignKey(News.id,ondelete="CASCADE"), nullable=False, comment="新闻ID")
    def __repr__(self):
        return f"Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id},created_at={self.created_at})"