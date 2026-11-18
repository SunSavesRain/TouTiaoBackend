from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from enums.user import Gender, UserRole

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    phone: str | None = None
    nickname: str | None = None
    avatar: str | None = None
    gender: Gender = Gender.unknown
    bio: str | None = None

class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field(None,max_length=50,description="用户昵称")
    avatar: Optional[str] = Field(None,max_length=255,description="用户头像URL")
    gender: Gender | None = None
    bio: Optional[str] = Field(None,max_length=500,description="个人简介")

class UserUpdate(UserInfoBase):
    phone: str | None = None

class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)

class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")
    model_config = ConfigDict(populate_by_name=True,#适应user_info的别名，alias和字段名兼容
                              from_attributes=True #允许user_info从orm对象中获取数据
                              )

class UpdateUserPassword(BaseModel):
    old_password: str = Field(..., alias="oldPassword")
    new_password: str = Field(..., alias="newPassword")
