from pydantic import BaseModel, Field, ConfigDict

class DashboardStats(BaseModel):
    news: int
    users: int
    comments: int
    views: int

class VisitTrendItem(BaseModel):
    date: str
    views: int

class CategoryDistributionItem(BaseModel):
    name: str
    value: int

class HotNewsItem(BaseModel):
    id: int
    title: str
    category: str
    views: int
    comments: int

class DashboardResponse(BaseModel):
    stats: DashboardStats
    visit_trend: list[VisitTrendItem] = Field(alias="visitTrend")
    category_distribution: list[CategoryDistributionItem] = Field(alias="categoryDistribution")
    hot_news: list[HotNewsItem] = Field(alias="hotNews")
    model_config = ConfigDict(populate_by_name=True)