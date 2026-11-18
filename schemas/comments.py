from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CommentCreate(BaseModel):
    news_id: int = Field(alias="newsId")
    content: str = Field(..., min_length=1, max_length=500)
    model_config = ConfigDict(populate_by_name=True)

class CommentItem(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    username: str
    avatar: str | None = None
    nickname: str | None = None
    content: str
    created_at: datetime = Field(alias="createdAt")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class CommentListResponse(BaseModel):
    list: list[CommentItem]
    total: int
    has_more: bool = Field(..., alias="hasMore")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)