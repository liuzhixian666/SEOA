from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
import logging

# 初始化FastAPI应用
app = FastAPI()

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 初始化数据库
init_db()

# 配置logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入各个模块并注册路由
from auth import register_router as register_auth_router
from classes import register_router as register_classes_router
from exams import register_router as register_exams_router
from conversations import register_router as register_conversations_router
from templates import register_router as register_templates_router
from notifications import register_router as register_notifications_router

# 注册路由
register_auth_router(app)
register_classes_router(app)
register_exams_router(app)
register_conversations_router(app)
register_templates_router(app)
register_notifications_router(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

#注意：无法启动先安装各种软件包，在检查Database中的账号信息与主机信息是否一致

#登录默认账号：13800138000       密码：test123