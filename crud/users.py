from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from fastapi.encoders import jsonable_encoder
from cache.users_cache import get_cache_by_token, set_cache_by_token
from models.users import User,UserToken
from schemas.users import UserCreate, UserUpdate, UpdateUserPassword
from utils import security
import uuid
from  utils.security import verify_password
#根据用户名查找用户
async def get_users_by_username(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

#用户注册
async def create_user(db: AsyncSession,user_data: UserCreate):
    hashed_password = security.get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password=hashed_password,
        phone=user_data.phone,
        nickname=user_data.nickname,
        avatar=user_data.avatar,
        gender=user_data.gender,
        bio=user_data.bio
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

#生成用户token
async def generate_user_token(db: AsyncSession, user_id: int):
    token=str(uuid.uuid4())
    expire_date = datetime.now() + timedelta(days=7)
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    existing_token = result.scalar_one_or_none()
    if existing_token:
        existing_token.token = token
        existing_token.expires_at = expire_date
    else:
        new_token = UserToken(
            user_id=user_id,
            token=token,
            expires_at=expire_date
        )
        db.add(new_token)
    await db.commit()
    return token

#根据用户id删除token
async def delete_user_token(db: AsyncSession, user_id: int):
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()
    if user_token is None:
        return True
    await db.delete(user_token)
    await db.commit()
    return True


#判断用户名和密码是否正确
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_users_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

#根据token获取用户信息
async def get_user_by_token(db: AsyncSession, token: str):
    cache_user = await get_cache_by_token(token)
    if cache_user:
        return User(**cache_user)
    stmt = select(UserToken).where(UserToken.token == token)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()
    if not user_token or user_token.expires_at < datetime.now():
        return "401"
    stmt = select(User).where(User.id == user_token.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        await set_cache_by_token(token,jsonable_encoder(user))
    return user

#根据用户名更新用户信息
async def update_user_info(db: AsyncSession, username: str, user_data: UserUpdate):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    old_avatar = user.avatar
    #把pydantic类型转换为字典并展开
    stmt = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,#只更新传入的字段
        exclude_none=True#值为None的字段不更新
    ))
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户更新失败")
    return await get_users_by_username(db, username), old_avatar

#根据用户名更新用户密码
async def update_user_password(db: AsyncSession, user: User,password_data: UpdateUserPassword):
    if not verify_password(password_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")
    hashed_new_password = security.get_password_hash(password_data.new_password)
    user.password = hashed_new_password
    await db.commit()
    return True