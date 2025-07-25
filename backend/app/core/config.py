"""
配置模块

包含应用程序的配置设置
"""

import os
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 先创建Base，避免循环导入
Base = declarative_base()

class Settings(BaseModel):
    """应用程序设置"""
    
    # 应用程序名称
    APP_NAME: str = "AI HTML学习平台"
    
    # API版本
    API_V1_STR: str = "/api"
    
    # CORS设置 (跨域资源共享)
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # 在生产环境中，应该限制为实际前端URL，例如:
    # BACKEND_CORS_ORIGINS: list = [
    #     "http://localhost:3000",
    #     "http://localhost:8080",
    # ]
    
    # 日志级别
    LOG_LEVEL: str = "DEBUG"

# 从环境变量获取数据库配置，如果不存在则使用默认值
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "HTML_AI")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=True,  # 可选，调试用
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表的函数
def create_tables():
    """创建所有数据库表"""
    # 在函数内部导入models，避免循环导入
    from . import models
    Base.metadata.create_all(bind=engine)

# 创建全局设置对象
settings = Settings()

# 数据库依赖项
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()