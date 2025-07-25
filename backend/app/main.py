"""
AI HTML学习平台后端
主应用入口文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
# 优先加载根目录的.env文件
root_env_path = Path(__file__).parent.parent.parent / '.env'
backend_env_path = Path(__file__).parent.parent / '.env'
env_path = root_env_path if root_env_path.exists() else backend_env_path

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logging.info(f"已加载环境变量文件: {env_path}")
    logging.info(f"OPENAI_API_KEY: {openai_key[:10] if (openai_key := __import__('os').environ.get('OPENAI_API_KEY')) else 'Not set'}")
    logging.info(f"OPENAI_API_BASE: {__import__('os').environ.get('OPENAI_API_BASE', 'Not set')}")
    logging.info(f"OPENAI_MODEL: {__import__('os').environ.get('OPENAI_MODEL', 'Not set')}")

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
    import os
    logger.info("启动AI HTML学习平台后端")
    # 从环境变量获取端口配置，如果没有设置则使用默认值8000
    # 开发者注意：请在项目根目录的.env文件中配置端口，而非修改此处硬编码
    port = int(os.environ.get("BACKEND_PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)