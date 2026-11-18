from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from schemas.news import NewsItem

class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

class HistoryAddResponse(BaseModel):
    id: int
    user_id: int = Field(..., alias="userId")
    news_id: int = Field(..., alias="newsId")
    view_time: datetime = Field(..., alias="viewTime")
    model_config = ConfigDict(populate_by_name=True,
                              from_attributes=True)

class HistoryListItem(NewsItem):
    view_time: datetime = Field(..., alias="viewTime")
    model_config = ConfigDict(populate_by_name=True,
                              from_attributes=True)

class HistoryListResponse(BaseModel):
    list: list[HistoryListItem]
    total: int
    has_more: bool = Field(...,alias="hasMore")
    model_config = ConfigDict(populate_by_name=True,
                              from_attributes=True)