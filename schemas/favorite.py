from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from schemas.news import NewsItem
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

class FavoriteAddResponse(BaseModel):
    id: int
    user_id: int = Field(..., alias="userId")
    news_id: int = Field(..., alias="newsId")
    created_at: datetime = Field(..., alias="createTime")
    model_config = ConfigDict(populate_by_name=True,  # 适应user_info的别名，alias和字段名兼容
                              from_attributes=True  # 允许user_info从orm对象中获取数据
                              )

class FavoriteNewsItem(NewsItem):
    favorite_id: int = Field(...,alias="favoriteId")
    favorite_time: datetime = Field(..., alias="favoriteTime")
    model_config = ConfigDict(populate_by_name=True,
                              from_attributes=True
                              )

class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItem]
    total: int
    has_more: bool = Field(...,alias="hasMore")
    model_config = ConfigDict(populate_by_name=True,
                              from_attributes=True
                              )