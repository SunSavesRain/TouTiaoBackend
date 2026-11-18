from datetime import datetime, date
from sqlalchemy import DateTime, Index, Date
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


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

class DailyVisitStats(Base):
    __tablename__ = "daily_visit_stats"
    __table_args__ = (Index("uk_daily_visit_date","stat_date",unique=True),)
    id: Mapped[int] = mapped_column(INTEGER(unsigned=True),primary_key=True,autoincrement=True,comment="统计ID")
    stat_date: Mapped[date] = mapped_column(Date,nullable=False,comment="统计日期")
    views: Mapped[int] = mapped_column(INTEGER(unsigned=True),nullable=False,default=0,comment="当日访问量")

    def __repr__(self):
        return f"<DailyVisitStats(id={self.id}, stat_date={self.stat_date}, views={self.views})>"
