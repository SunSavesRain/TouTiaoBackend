from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Text, Index, ForeignKey,Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Enum as SqlEnum
from enums.news import NewsStatus


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
class Category(Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(Integer,primary_key=True, comment="分类ID",autoincrement=True)
    name: Mapped[str] = mapped_column(String(50),nullable=False,comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer,default=0,nullable=False,comment="排序")
    enabled: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False,comment="是否启用")

    def __repr__(self):
        return f"Category(id={self.id},name={self.name},sort_order={self.sort_order})"
class News(Base):
    __tablename__ = "news"
    __table_args__ = (
        Index("fk_news_category_idx", "category_id"),
        Index('idx_publish_time', 'publish_time')
    )
    id: Mapped[int] = mapped_column(Integer,primary_key=True, comment="新闻ID",autoincrement=True)
    title: Mapped[str] = mapped_column(String(255),nullable=False,comment="新闻标题")
    content: Mapped[str] = mapped_column(Text,nullable=False,comment="新闻内容")
    category_id: Mapped[int] = mapped_column(Integer,ForeignKey("news_category.id"),nullable=False,comment="分类ID")
    description: Mapped[Optional[str]] = mapped_column(String(500),nullable=True,comment="新闻描述")
    image: Mapped[Optional[str]] = mapped_column(String(255),nullable=True,comment="新闻图片URL")
    author: Mapped[Optional[str]] = mapped_column(String(50),nullable=True,comment="新闻作者")
    views: Mapped[int] = mapped_column(Integer,default=0,nullable=False,comment="浏览量")
    status: Mapped[NewsStatus] = mapped_column(SqlEnum(NewsStatus),nullable=False,default=NewsStatus.published,comment="新闻状态")
    publish_time: Mapped[datetime | None] = mapped_column(DateTime,nullable=True,comment="发布时间")
    def __repr__(self):
        return f"News(id={self.id},title={self.title},content={self.content},category_id={self.category_id},description={self.description},image={self.image},author={self.author},views={self.views},publish_time={self.publish_time})"
