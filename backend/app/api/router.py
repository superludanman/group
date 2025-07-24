"""
API路由模块
包含所有API端点的路由定义
"""

from fastapi import APIRouter, Request
import logging

# 导入模块处理程序
from app.modules.module_loader import (
    get_module_handler,
    post_module_handler
)
from app.core.models import UserKnowledge
from app.core.config import SessionLocal
from app.core.knowledge_map import knowledge_map
from sqlalchemy.orm import Session
from fastapi import HTTPException

# 配置日志
logger = logging.getLogger(__name__)

# 创建API路由器
api_router = APIRouter()

# 健康检查端点
@api_router.get("/health")
async def health_check():
    """
    健康检查端点，用于验证API是否正常运行
    """
    return {"status": "ok"}

# 模块API端点
@api_router.get("/module/{module_name}")
async def get_module(module_name: str):
    """
    模块数据获取API端点
    每个模块可以实现自己的数据获取逻辑
    
    参数:
        module_name: 模块名称
        
    返回:
        模块数据响应
    """
    handler = get_module_handler(module_name)
    if handler:
        return await handler()
    else:
        return {"module": module_name, "status": "模块未找到或未注册"}

@api_router.post("/module/{module_name}")
async def post_module(module_name: str, request: Request):
    """
    模块数据处理API端点
    每个模块可以实现自己的数据处理逻辑
    
    参数:
        module_name: 模块名称
        request: 请求对象，包含客户端发送的数据
        
    返回:
        模块处理响应
    """
    handler = post_module_handler(module_name)
    if handler:
        return await handler(request)
    else:
        return {"module": module_name, "status": "模块未找到或未注册"}

@api_router.post("/users/{user_id}/knowledge")
async def learn_knowledge(user_id: str, request: Request):
    data = await request.json()
    knowledge_id = data["knowledge_id"]
    db: Session = SessionLocal()
    try:
        exists = db.query(UserKnowledge).filter_by(user_id=user_id, knowledge_id=knowledge_id).first()
        if not exists:
            record = UserKnowledge(user_id=user_id, knowledge_id=knowledge_id)
            db.add(record)
            db.commit()
        return {"status": "ok"}
    finally:
        db.close()

@api_router.get("/users/{user_id}/allowed-tags")
async def get_allowed_tags(user_id: str):
    db: Session = SessionLocal()
    try:
        learned = db.query(UserKnowledge).filter_by(user_id=user_id).all()
        # 如果没有学习记录，自动添加 html_base
        if not learned:
            record = UserKnowledge(user_id=user_id, knowledge_id="html_base")
            db.add(record)
            db.commit()
            learned = [record]
        tags = set()
        for rec in learned:
            tags.update(knowledge_map.get(rec.knowledge_id, []))
        return {"allowed_tags": list(tags)}
    finally:
        db.close()

@api_router.post("/emotion")
async def emotion(request: Request):
    """
    情绪分析API端点
    """
    response = await request.json()
    text = response["text"]
    return await EmotionModel(text)
