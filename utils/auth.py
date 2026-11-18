from fastapi import Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud.users import get_user_by_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from enums.user import UserRole, UserStatus
from models.users import User

security = HTTPBearer()

#获取token
def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return credentials.credentials

#根据token查询并返回用户
async def get_current_user(db: AsyncSession=Depends(get_database), token: str = Depends(get_current_token)):
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    if user=="401":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户未授权")
    if user.status == UserStatus.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用")
    return user

#判断用户是否为管理员
async def get_current_admin(user: User = Depends(get_current_user)):
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="用户不是管理员")
    return user
