"""
配置模块

包含应用程序的配置设置
"""

import os
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

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
    LOG_LEVEL: str = "INFO"

# MySQL数据库连接URL（请替换为你的实际信息）
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345678@localhost:3306/HTML_AI?charset=utf8mb4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=True,  # 可选，调试用
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 创建全局设置对象
settings = Settings()