from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from models.news import News, Category
from schemas.admin.category import AdminCategoryCreate, AdminCategoryUpdate


# 获取所有分类和对应的新闻总数
async def get_all_categories(db: AsyncSession):
    #outerjoin用于新闻表中没有这个分类的新闻也能显示出来,先连接合并两个表，然后按照分类分组，查询每类的新闻总数和分类信息
    #因为select同时包含聚合函数和普通字段，所以group要包含所有普通字段
    stmt = (select(Category.id, Category.name,Category.sort_order,Category.enabled,
                  func.count(News.id).label("news_count")).outerjoin(News, Category.id == News.category_id)
                  .group_by(Category.id,Category.name,Category.sort_order,Category.enabled).
                  order_by(Category.sort_order.asc(), Category.id.asc()))
    result = await db.execute(stmt)
    return result.mappings().all()

#增加新闻分类
async def add_category(db: AsyncSession,category_data: AdminCategoryCreate):
    stmt = select(Category).where(Category.name == category_data.name)
    result = await db.execute(stmt)
    existing_category = result.scalar_one_or_none()
    if existing_category:
        raise HTTPException(status_code=400, detail="分类已存在")
    category = Category(name=category_data.name, sort_order=category_data.sort_order,
                        enabled=category_data.enabled)
    db.add(category)
    await db.commit()
    return category

#更新新闻分类
async def update_category(db: AsyncSession,category_id: int,category_data: AdminCategoryUpdate):
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    if category_data.name is not None:
        stmt = select(Category).where(Category.name == category_data.name,Category.id != category_id)
        result = await db.execute(stmt)
        existing_category = result.scalar_one_or_none()
        if existing_category:
            raise HTTPException(status_code=400, detail="分类名称重复")
    update_data = category_data.model_dump(exclude_unset=True,by_alias=False)
    #将update_data中的键值对更新到category中
    for key, value in update_data.items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category

#查询分类下的新闻数量
async def get_category_news_count(db: AsyncSession,category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

#删除新闻分类
async def delete_category(db: AsyncSession,category_id: int):
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    count = await get_category_news_count(db, category_id)
    if count > 0:
        raise HTTPException(status_code=400, detail="分类下有新闻，不能删除")
    await db.delete(category)
    await db.commit()
    return True
