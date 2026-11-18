from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class AdminCommentResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    username: str
    nickname: str | None = None
    news_id: int = Field(alias="newsId")
    news_title: str = Field(alias="newsTitle")
    content: str
    created_at: datetime = Field(alias="createdAt")
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

class AdminCommentListResponse(BaseModel):
    list: list[AdminCommentResponse]
    total: int
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)