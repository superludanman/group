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

# 导入IDE模块的额外处理程序
from app.modules.ide_module import (
    ai_chat_handler,
    ai_error_feedback_handler,
    student_update_handler,
    get_student_model_handler
)

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

# IDE模块特定的API端点
@api_router.post("/module/ide/ai/chat")
async def ide_ai_chat(request: Request):
    """
    IDE模块AI聊天端点
    """
    return await ai_chat_handler(request)

@api_router.post("/module/ide/ai/error-feedback")
async def ide_ai_error_feedback(request: Request):
    """
    IDE模块AI错误反馈端点
    """
    return await ai_error_feedback_handler(request)

@api_router.post("/module/ide/student/update")
async def ide_student_update(request: Request):
    """
    IDE模块学生模型更新端点
    """
    return await student_update_handler(request)

@api_router.get("/module/ide/student/{session_id}")
async def ide_get_student_model(session_id: str, request: Request):
    """
    IDE模块获取学生模型端点
    """
    # 为处理程序添加路径参数
    request.path_params = {"session_id": session_id}
    return await get_student_model_handler(request)