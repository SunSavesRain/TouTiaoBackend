from fastapi import APIRouter, Depends, Query,UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud.admin.news import get_admin_news_list, get_admin_news_by_id, add_admin_news, update_admin_news, \
    delete_admin_news
from enums.news import NewsStatus
from schemas.admin.news import AdminNewsListItem, AdminNewsListResponse, AdminNewsDetailResponse, AdminNewsCreate, \
    AdminNewsUpdate
from utils.auth import get_current_admin
from utils.response import success_response
import os
import uuid

NEWS_IMAGE_DIR = "static/news"
os.makedirs(NEWS_IMAGE_DIR, exist_ok=True)
router = APIRouter(
    prefix="/api/admin/news",
    tags=["后台-新闻管理"],
    dependencies=[Depends(get_current_admin)]
)

# 删除新闻图片
def delete_news_image(image_url: str | None):
    if not image_url:
        return
    prefix = "/static/news/"
    # 只允许删除我们自己的新闻图片
    if not image_url.startswith(prefix):
        return
    filename = image_url.removeprefix(prefix)
    file_path = os.path.join(NEWS_IMAGE_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

# 后台获取新闻列表
@router.get("")
async def get_news_list_api(
        keyword: str | None = Query(default=None),
        category_id: int | None = Query(default=None, alias="categoryId"),
        status: NewsStatus | None = Query(default=None),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=8, alias="pageSize", ge=1, le=100),
        db: AsyncSession = Depends(get_database)
):
    news, total = await get_admin_news_list(db,keyword,page, page_size,category_id,status)
    news_list = [AdminNewsListItem.model_validate(item) for item in news]
    data = AdminNewsListResponse(list=news_list, total=total)
    return success_response(data=data, message="获取新闻列表成功")

# 后台获取新闻详情
@router.get("/{news_id}")
async def get_news_detail_api(news_id: int, db: AsyncSession = Depends(get_database)):
    new = await get_admin_news_by_id(db, news_id)
    data = AdminNewsDetailResponse.model_validate(new)
    return success_response(data=data, message="获取新闻详情成功")

# 上传新闻图片
@router.post("/image")
async def upload_news_image(file: UploadFile = File(...)):
    allowed_types = {"image/jpeg","image/png","image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400,detail="仅支持 JPG、PNG、WEBP 图片")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400,detail="图片大小不能超过5MB")
    original_filename = file.filename or ""
    suffix = os.path.splitext(original_filename)[1].lower()
    filename = f"{uuid.uuid4()}{suffix}"
    file_path = os.path.join(NEWS_IMAGE_DIR,filename)
    with open(file_path, "wb") as f: f.write(content)
    image_url = f"/static/news/{filename}"
    return success_response(data={"url": image_url},message="图片上传成功")

#新增新闻
@router.post("")
async def add_news_api(news_data: AdminNewsCreate, db: AsyncSession = Depends(get_database)):
    news,category_name = await add_admin_news(db, news_data)
    data = AdminNewsDetailResponse(id=news.id,title=news.title,category_id=news.category_id,
        category=category_name,author=news.author,description=news.description,
        content=news.content,image=news.image,views=news.views,
        status=news.status,publish_time=news.publish_time)
    return success_response(data=data, message="新增新闻成功")

#修改新闻
@router.put("/{news_id}")
async def update_admin_news_api(news_id: int,news_data: AdminNewsUpdate,db: AsyncSession = Depends(get_database)):
    news,category_name,old_image = await update_admin_news(db, news_id, news_data)
    if (old_image and news.image != old_image):
        delete_news_image(old_image)
    data = AdminNewsDetailResponse(id=news.id,title=news.title,category_id=news.category_id,
        category=category_name,author=news.author,description=news.description,content=news.content,
        image=news.image,views=news.views,status=news.status,publish_time=news.publish_time)
    return success_response(data=data, message="修改新闻成功")

#删除新闻
@router.delete("/{news_id}")
async def delete_news_api(news_id: int, db: AsyncSession = Depends(get_database)):
    old_image = await delete_admin_news(db, news_id)
    delete_news_image(old_image)
    return success_response(message="删除新闻成功")




