from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enums.user import UserRole, UserStatus, Gender

class AdminUserListItem(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    role: UserRole
    status: UserStatus
    phone: str | None = None
    gender: Gender
    avatar: str | None = None
    created_at: datetime = Field(alias="createdAt")
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

class AdminUserDetailResponse(AdminUserListItem):
    bio: str | None = None
    updated_at: datetime = Field(alias="updatedAt")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class AdminUserListResponse(BaseModel):
    list: list[AdminUserListItem]
    total: int
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class AdminUserRoleUpdate(BaseModel):
    role: UserRole
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class AdminUserPasswordUpdate(BaseModel):
    password: str
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class AdminUserStatusUpdate(BaseModel):
    status: UserStatus
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
