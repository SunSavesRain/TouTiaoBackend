from config.cache_config import get_cache_json, set_cache,redis_client
from typing import List, Dict, Any, Optional

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news:list"
NEWS_DETAIL_PREFIX = "news:detail"
NEWS_RELATED_PREFIX = "news:related"
HOT_SEARCH_KEY = "news:hot_search"

#获取新闻分类缓存
async def get_cache_categories():
    return await get_cache_json(CATEGORIES_KEY)

#写入新闻分类缓存
async def set_cache_categories(data: List[Dict[str,Any]], expire: int = 7200):
    result = await set_cache(CATEGORIES_KEY,data,expire)
    return result

#写入新闻列表缓存
async def set_cache_news_list(category_id: Optional[int],page: int,page_size: int,data: List[Dict[str,Any]], expire: int = 1800):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{page_size}"
    result = await set_cache(key,data,expire)
    return result

#读取新闻列表缓存
async def get_cache_news_list(category_id: Optional[int],page: int,page_size: int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{page_size}"
    return await get_cache_json(key)

#写入新闻详情缓存
async def set_cache_news_detail(news_id: int,data: Dict[str,Any], expire: int = 1800):
    key = f"{NEWS_DETAIL_PREFIX}:{news_id}"
    result = await set_cache(key,data,expire)
    return result

#读取新闻详情缓存
async def get_cache_news_detail(news_id: int):
    key = f"{NEWS_DETAIL_PREFIX}:{news_id}"
    return await get_cache_json(key)

#写入相关新闻缓存
async def set_cache_news_related(news_id: int,category_id: int,data: List[Dict[str,Any]],limit: int = 5,expire: int = 1800):
    key = f"{NEWS_RELATED_PREFIX}:{news_id}:{category_id}:{limit}"
    result = await set_cache(key,data,expire)
    return result

#读取相关新闻缓存
async def get_cache_news_related(news_id: int,category_id: int,limit: int = 5):
    key = f"{NEWS_RELATED_PREFIX}:{news_id}:{category_id}:{limit}"
    return await get_cache_json(key)

# 增加热门搜索关键词的搜索次数
async def increment_hot_search(keyword: str):
    try:
        await redis_client.zincrby(HOT_SEARCH_KEY, 1, keyword)
        return True
    except Exception as e:
        print(f"增加热门搜索次数失败：{e}")
        return False
# 获取热门搜索关键词
async def get_hot_search(limit: int = 10):
    try:
        #withscores=True表示除了关键词本身，还把它的 score 一起返回
        result = await redis_client.zrevrange(HOT_SEARCH_KEY,0,limit - 1,withscores=True)
        return [{"keyword": keyword,"count": int(score)} for keyword, score in result]
    except Exception as e:
        print(f"获取热门搜索失败：{e}")
        return []

#删除新闻缓存
async def delete_cache_news_detail(news_id: int):
    key = f"{NEWS_DETAIL_PREFIX}:{news_id}"
    await redis_client.delete(key)
    return True

# 删除所有新闻列表缓存
async def delete_cache_news_list():
    pattern = f"{NEWS_LIST_PREFIX}:*"
    async for key in redis_client.scan_iter(match=pattern):
        await redis_client.delete(key)
    return True

# 删除所有相关新闻缓存
async def delete_cache_news_related():
    pattern = f"{NEWS_RELATED_PREFIX}:*"
    async for key in redis_client.scan_iter(match=pattern):
        await redis_client.delete(key)
    return True
