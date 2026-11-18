from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func,or_, and_
from fastapi import HTTPException
from enums.user import Gender, UserRole,UserStatus
from models.users import User
from schemas.admin.users import AdminUserPasswordUpdate
from utils import security

#搜索用户
async def get_admin_users_list(db: AsyncSession,keyword: str | None = None,page: int = 1,page_size: int = 8,
                      role: UserRole | None = None,status: UserStatus | None = None,gender: Gender | None = None):
    conditions = []
    if keyword:
        keywords = keyword.strip().split()
        for word in keywords:
            keyword_pattern = f"%{word}%"
            conditions.append(or_(User.username.like(keyword_pattern),User.nickname.like(keyword_pattern)))
    if role is not None:
        conditions.append(User.role == role)
    if status is not None:
        conditions.append(User.status == status)
    if gender is not None:
        conditions.append(User.gender == gender)
    offset = (page - 1) * page_size
    stmt = (select(User).order_by(User.id.desc()).limit(page_size).offset(offset))
    count_stmt = select(func.count(User.id))
    if conditions:
        condition = and_(*conditions)
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    result = await db.execute(stmt)
    user_list = result.scalars().all()
    count_result = await db.execute(count_stmt)
    return user_list, count_result.scalar_one()

#获取用户详情
async def get_admin_user_detail(db: AsyncSession, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

#更新用户角色
async def update_admin_user_role(db: AsyncSession, user_id: int, role: UserRole):
    user = await get_admin_user_detail(db, user_id)
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user

#更新用户状态
async def update_admin_user_status(db: AsyncSession, user_id: int, status: UserStatus):
    user = await get_admin_user_detail(db, user_id)
    user.status = status
    await db.commit()
    await db.refresh(user)
    return user

#删除用户
async def delete_admin_user(db: AsyncSession, user_id: int):
    user = await get_admin_user_detail(db, user_id)
    avatar = user.avatar
    await db.delete(user)
    await db.commit()
    return avatar

#修改密码
async def update_admin_user_password(db: AsyncSession, user_id: int, password_data: AdminUserPasswordUpdate):
    user = await get_admin_user_detail(db, user_id)
    hashed_new_password = security.get_password_hash(password_data.password)
    user.password = hashed_new_password
    await db.commit()
    await db.refresh(user)
    return user


