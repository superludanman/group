"""
AI HTML学习平台后端
主应用入口文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

# 导入API路由
from app.api.router import api_router

# 导入模块加载器
from app.modules.module_loader import (
    load_all_modules,
    create_example_modules
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="AI HTML学习平台", description="ACM CHI项目的后端API")

# 配置CORS（跨域资源共享）
# 这允许前端（可能在不同的端口或域上运行）访问后端API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为实际前端URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含所有API路由
app.include_router(api_router, prefix="/api")

# 启动时加载所有模块
@app.on_event("startup")
async def startup_event():
    logger.info("加载模块...")
    # 如果模块模板不存在，则创建示例模块模板
    create_example_modules()
    # 加载所有模块
    load_all_modules()
    logger.info("应用启动完成")

# 主入口点
if __name__ == "__main__":
    logger.info("启动AI HTML学习平台后端")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)