from fastapi import APIRouter, Depends, Query,UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from cache.users_cache import delete_cache_by_user_id
from config.db_config import get_database
from crud.users import delete_user_token
from schemas.admin.users import AdminUserListItem, AdminUserListResponse, AdminUserDetailResponse, AdminUserRoleUpdate, \
    AdminUserStatusUpdate, AdminUserPasswordUpdate
from utils.auth import get_current_admin
from utils.response import success_response
from enums.user import Gender, UserRole,UserStatus
from crud.admin.users import get_admin_users_list, get_admin_user_detail, update_admin_user_role, \
    update_admin_user_status, delete_admin_user, update_admin_user_password
from models.users import User

import os
router = APIRouter(
    prefix="/api/admin/users",
    tags=["后台-用户管理"],
    dependencies=[Depends(get_current_admin)]
)

AVATAR_IMAGE_DIR = "static/avatars"
os.makedirs(AVATAR_IMAGE_DIR, exist_ok=True)

# 删除用户头像
def delete_user_avatar(image_url: str | None):
    if not image_url:
        return
    prefix = "/static/avatars/"
    if not image_url.startswith(prefix):
        return
    filename = image_url.removeprefix(prefix)
    file_path = os.path.join(AVATAR_IMAGE_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

#后台获取用户列表
@router.get("")
async def get_users_list_api(
        keyword: str | None = Query(default=None),
        role: UserRole | None = Query(default=None),
        status: UserStatus | None = Query(default=None),
        gender: Gender | None = Query(default=None),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=8, alias="pageSize", ge=1, le=100),
        db: AsyncSession = Depends(get_database)):
    users, total = await get_admin_users_list(db, keyword,page, page_size, role, status, gender)
    user_list = [AdminUserListItem.model_validate(item) for item in users]
    data = AdminUserListResponse(list=user_list, total=total)
    return success_response(data=data, message="获取用户列表成功")

#后台获取用户详情
@router.get("/{user_id}")
async def get_user_detail_api(user_id: int, db: AsyncSession = Depends(get_database)):
    user = await get_admin_user_detail(db, user_id)
    return success_response(data=AdminUserDetailResponse.model_validate(user), message="获取用户详情成功")

#后台更新用户角色
@router.patch("/{user_id}/role")
async def update_user_role_api(user_id: int,data: AdminUserRoleUpdate,db: AsyncSession = Depends(get_database),
                               current_admin: User = Depends(get_current_admin)):
    if user_id == current_admin.id and data.role != UserRole.admin:
        raise HTTPException(status_code=400, detail="不能修改自己的管理员角色")
    user = await update_admin_user_role(db, user_id, data.role)
    await delete_cache_by_user_id(db, user_id)
    return success_response(data=AdminUserDetailResponse.model_validate(user), message="更新用户角色成功")

#后台更新用户状态
@router.patch("/{user_id}/status")
async def update_user_status_api(user_id: int,data: AdminUserStatusUpdate,db: AsyncSession = Depends(get_database),
                                 current_admin: User = Depends(get_current_admin)):
    if user_id == current_admin.id and data.status == UserStatus.disabled:
        raise HTTPException(status_code=400, detail="不能禁用当前登录的管理员账号")
    user = await update_admin_user_status(db, user_id, data.status)
    await delete_cache_by_user_id(db, user_id)
    return success_response(data=AdminUserDetailResponse.model_validate(user), message="更新用户状态成功")

#删除用户
@router.delete("/{user_id}")
async def delete_user_api(user_id: int, db: AsyncSession = Depends(get_database), current_admin: User = Depends(get_current_admin)):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录的管理员账号")
    await delete_cache_by_user_id(db, user_id)
    old_image = await delete_admin_user(db, user_id)
    delete_user_avatar(old_image)
    return success_response(message="删除用户成功")

#后台更新用户密码
@router.patch("/{user_id}/password")
async def update_user_password_api(user_id: int, data: AdminUserPasswordUpdate, db: AsyncSession = Depends(get_database)):
    await update_admin_user_password(db, user_id, data)
    await delete_cache_by_user_id(db, user_id)
    await delete_user_token(db, user_id)
    return success_response(message="更新用户密码成功")
