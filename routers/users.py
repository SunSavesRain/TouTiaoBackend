from fastapi import APIRouter, Depends,HTTPException, status,UploadFile,File
from sqlalchemy.ext.asyncio import AsyncSession
from cache.users_cache import delete_cache_by_token
from config.db_config import get_database
from crud.users import get_users_by_username, create_user, generate_user_token, authenticate_user, update_user_info, \
    update_user_password, delete_user_token
from enums.user import UserStatus
from schemas.users import UserCreate, UserAuthResponse, UserInfoResponse, UserLogin, UserUpdate, UpdateUserPassword
from utils.auth import get_current_user, get_current_token
from utils.response import success_response
from models.users import User
import uuid
import os
router = APIRouter(prefix="/api/user", tags=["users"])
AVATAR_DIR = "static/avatars"
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg","image/png": ".png","image/webp": ".webp"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024

# 删除用户头像
def delete_user_avatar(image_url: str | None):
    if not image_url:
        return
    prefix = "/static/avatars/"
    if not image_url.startswith(prefix):
        return
    filename = image_url.removeprefix(prefix)
    file_path = os.path.join(AVATAR_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

# 用户注册接口
@router.post("/register")
async def register_user_api(db: AsyncSession = Depends(get_database), user_data: UserCreate = None):
    if not user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户注册数据非法")
    existing_user = await get_users_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    new_user = await create_user(db, user_data)
    token = await generate_user_token(db, new_user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(new_user))
    return success_response(message="注册成功", data=response_data)

# 用户登录接口
@router.post("/login")
async def login_user_api(db: AsyncSession = Depends(get_database), user_data: UserLogin = None):
    if not user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户登录数据非法")
    user = await authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if user.status == UserStatus.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户已禁用")
    token = await generate_user_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)

# 获取用户信息接口
@router.get("/info")
async def get_user_info_api(user: User= Depends(get_current_user)):
    response_data = UserInfoResponse.model_validate(user)
    return success_response(message="获取用户信息成功", data=response_data)

#更新用户信息接口
@router.put("/update")
async def update_user_info_api(db: AsyncSession = Depends(get_database), user: User= Depends(get_current_user),
                               user_data: UserUpdate = None,token: str = Depends(get_current_token)):
    if not user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户更新数据非法")
    result,old_avatar = await update_user_info(db, user.username, user_data)
    delete_user_avatar(old_avatar)
    response_data = UserInfoResponse.model_validate(result)
    await delete_cache_by_token(token)
    return success_response(message="更新用户信息成功", data=response_data)

#更新用户密码接口
@router.put("/password")
async def update_user_password_api(db: AsyncSession = Depends(get_database), user: User= Depends(get_current_user),
    password_data: UpdateUserPassword = None,token: str = Depends(get_current_token)):
    if not password_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户密码更新数据非法")
    result = await update_user_password(db,user,password_data)
    if result:
        await delete_cache_by_token(token)
        await delete_user_token(db, user.id)
        return success_response(message="更新用户密码成功")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="出现异常情况")

#上传用户头像接口
@router.put("/avatar")
async def update_user_avatar_api(file: UploadFile = File(...),db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user),token: str = Depends(get_current_token)):
    content_type = file.content_type
    if content_type is None or content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、WEBP 图片")
    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="头像大小不能超过2MB")
    suffix = ALLOWED_IMAGE_TYPES[content_type]
    filename = f"{uuid.uuid4().hex}{suffix}"
    file_path = os.path.join(AVATAR_DIR, filename)
    try:
        with open(file_path, "wb") as f:f.write(content)
    except Exception:
        raise HTTPException(status_code=500, detail="头像保存失败")
    avatar = f"/static/avatars/{filename}"
    user_data = UserUpdate(avatar=avatar)
    updated_user, old_avatar = await update_user_info(db,user.username,user_data)
    delete_user_avatar(old_avatar)
    await delete_cache_by_token(token)
    return success_response(data={"avatar": updated_user.avatar},message="头像修改成功")
