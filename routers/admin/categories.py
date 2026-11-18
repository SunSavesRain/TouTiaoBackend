from fastapi import APIRouter, Depends, HTTPException
from crud.admin.category import get_all_categories, add_category, update_category, get_category_news_count, \
    delete_category
from schemas.admin.category import AdminCategoryResponse, AdminCategoryCreate, AdminCategoryUpdate
from utils.auth import get_current_admin
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from utils.response import success_response

router = APIRouter(
    prefix="/api/admin/categories",
    tags=["后台-分类管理"],
    dependencies=[Depends(get_current_admin)]
)

# 获取所有分类及对应的新闻总数
@router.get("")
async def get_categories_api(db: AsyncSession = Depends(get_database)):
    categories = await get_all_categories(db)
    data = [AdminCategoryResponse.model_validate(item) for item in categories]
    return success_response(
        data=data,
        message="获取分类列表成功"
    )

#新增分类
@router.post("")
async def add_category_api(category_data: AdminCategoryCreate,db: AsyncSession = Depends(get_database)):
    category = await add_category(db, category_data)
    if category:
        return success_response(
            data=AdminCategoryResponse(id=category.id,name=category.name,sort_order=category.sort_order,
                enabled=category.enabled,news_count=0),
            message="新增分类成功"
        )
    else:
        raise HTTPException(status_code=500, detail="新增分类失败")

#修改分类信息
@router.put("/{category_id}")
async def update_category_api(category_id: int, category_data: AdminCategoryUpdate,db: AsyncSession = Depends(get_database)):
    category = await update_category(db, category_id,category_data)
    count = await get_category_news_count(db, category_id)
    data=AdminCategoryResponse(id=category.id,name=category.name,sort_order=category.sort_order,
                enabled=category.enabled,news_count=count)
    if category:
        return success_response(data=data,message="修改分类信息成功")
    else:
        raise HTTPException(status_code=500, detail="修改分类信息失败")

#删除分类
@router.delete("/{category_id}")
async def delete_category_api(category_id: int,db: AsyncSession = Depends(get_database)):
    category = await delete_category(db, category_id)
    if category:
        return success_response(message="删除分类成功")
    else:
        raise HTTPException(status_code=500, detail="删除分类失败")


