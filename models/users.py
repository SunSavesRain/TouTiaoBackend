from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, Index, ForeignKey, Enum
from typing import Optional
from enums.user import UserRole, Gender, UserStatus
from sqlalchemy import Enum as SqlEnum

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

class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        Index("username_UNIQUE", "username"),
        Index("phone_UNIQUE", "phone")
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="用户ID", autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="用户名")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True, comment="手机号")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")
    status: Mapped[UserStatus] = mapped_column(SqlEnum(UserStatus),nullable=False,default=UserStatus.active,comment="用户状态")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="头像URL")
    gender: Mapped[Gender] = mapped_column(SqlEnum(Gender), nullable=False,default=Gender.unknown,comment="性别")
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="个人简介")
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), nullable=False,default=UserRole.user,comment="用户角色")

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, phone={self.phone}, nickname={self.nickname}, avatar={self.avatar}, bio={self.bio})"

class UserToken(Base):
    __tablename__ = "user_token"
    __table_args__ = (
        Index("token_UNIQUE", "token"),
        Index("fk_user_token_user_idx", "user_id")
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="用户TokenID", autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    token: Mapped[str] = mapped_column(String(255), nullable=False, comment="用户Token")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")

    def __repr__(self):
        return f"UserToken(id={self.id}, user_id={self.user_id}, token={self.token}, expires_at={self.expires_at})"