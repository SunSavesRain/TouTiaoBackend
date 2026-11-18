from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class NewsItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(None,alias="publishTime")
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

class NewsRelatedItemResponse(NewsItem):
    content: str
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

class NewsItemAll(NewsRelatedItemResponse):
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class NewsDetailResponse(NewsRelatedItemResponse):
    related_news: List[NewsRelatedItemResponse] = Field(default_factory=list,#默认值为空表
                                                alias="relatedNews")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class NewsListResponse(BaseModel):
    list: List[NewsItemAll]
    total: int
    has_more: bool = Field(...,alias="hasMore")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class ConNewsListResponse(BaseModel):
    list: List[NewsItemAll]
    total: int
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)