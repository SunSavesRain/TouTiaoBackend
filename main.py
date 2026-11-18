from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import news, users, favorate, history,comments
from utils.exception_handlers import register_exception_handlers
from fastapi.staticfiles import StaticFiles
from routers.admin import categories,dashboard
from routers.admin import comments as admin_comments
from routers.admin import news as admin_news
from routers.admin import users as admin_users


app = FastAPI()

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.mount("/static", StaticFiles(directory="static"), name="static")
#挂载/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorate.router)
app.include_router(history.router)
app.include_router(categories.router)
app.include_router(admin_comments.router)
app.include_router(comments.router)
app.include_router(dashboard.router)
app.include_router(admin_news.router)
app.include_router(admin_users.router)



