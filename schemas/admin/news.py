from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enums.news import NewsStatus


# 新增新闻
class AdminNewsCreate(BaseModel):
    title: str
    category_id: int = Field(alias="categoryId")
    author: str
    description: str | None = None
    content: str
    image: str | None = None
    status: NewsStatus = NewsStatus.draft
    model_config = ConfigDict(populate_by_name=True)

# 编辑新闻
class AdminNewsUpdate(BaseModel):
    title: str | None = None
    category_id: int | None = Field(None, alias="categoryId")
    author: str | None = None
    description: str | None = None
    content: str | None = None
    image: str | None = None
    status: NewsStatus | None = None
    model_config = ConfigDict(populate_by_name=True)

# 单独修改新闻状态
class AdminNewsStatusUpdate(BaseModel):
    status: NewsStatus

# 后台新闻列表中的一项
class AdminNewsListItem(BaseModel):
    id: int
    title: str
    category_id: int = Field(alias="categoryId")
    category: str
    author: str
    image: str | None = None
    views: int
    status: NewsStatus
    publish_time: datetime | None = Field(None, alias="publishTime")
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

# 新闻详情，用于后台点击“编辑”
class AdminNewsDetailResponse(AdminNewsListItem):
    description: str | None = None
    content: str

# 新闻列表分页结果
class AdminNewsListResponse(BaseModel):
    list: list[AdminNewsListItem]
    total: int
    model_config = ConfigDict(populate_by_name=True)