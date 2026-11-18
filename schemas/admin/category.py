from pydantic import BaseModel, Field, ConfigDict

class AdminCategoryCreate(BaseModel):
    name: str = Field(..., max_length=50)
    sort_order: int = Field(default=0, alias="sort")
    enabled: bool = True
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

class AdminCategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=50)
    sort_order: int | None = Field(None, alias="sort")
    enabled: bool | None = None
    model_config = ConfigDict(populate_by_name=True,from_attributes=True)

class AdminCategoryResponse(BaseModel):
    id: int
    name: str
    sort_order: int = Field(alias="sort")
    enabled: bool
    news_count: int = Field(alias="newsCount")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)



