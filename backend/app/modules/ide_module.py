"""
IDE 模块
此模块处理 AI HTML学习平台的 IDE 功能，包括代码编辑、预览和AI辅助功能。
"""

from typing import Dict, Any
from fastapi import Request
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 导入模块加载器
from .module_loader import register_module

# 导入代码执行器
try:
    from .ide_module_dir.code_executor import get_code_executor, CodeSubmission
    from .ide_module_dir.ai_service import get_ai_service
    from .ide_module_dir.student_model import get_student_model_service
    IDE_MODULE_AVAILABLE = True
    logger.info("成功导入IDE模块后端组件")
except Exception as e:
    logger.warning(f"无法导入IDE模块后端组件: {e}", exc_info=True)
    IDE_MODULE_AVAILABLE = False

# 获取代码执行器实例
code_executor = get_code_executor() if IDE_MODULE_AVAILABLE else None
if code_executor:
    logger.info("代码执行器实例化成功")
else:
    logger.warning("代码执行器实例化失败")

async def ai_chat(request: Request):
    """AI聊天功能"""
    # 检查模块是否可用
    if not IDE_MODULE_AVAILABLE:
        return {
            "status": "error",
            "message": "IDE模块不可用"
        }
    
    try:
        # 从请求获取JSON数据
        data = await request.json()
        message = data.get("message", "")
        code = data.get("code", {})
        session_id = data.get("session_id", "")
        
        # 获取AI服务实例
        ai_service = get_ai_service()
        
        # 获取学生模型服务
        student_model_service = get_student_model_service()
        
        # 获取学生模型
        student_model = student_model_service.get_model(session_id)
        model_summary = student_model_service.get_model_summary(session_id)
        
        # 准备代码上下文
        code_context = {
            "html": code.get("html", ""),
            "css": code.get("css", ""),
            "js": code.get("js", "")
        }
        
        # 获取AI响应
        response = await ai_service.get_ai_response(
            student_model_summary=model_summary,
            user_message=message,
            code_context=code_context
        )
        
        return {
            "status": "success",
            "reply": response.get("reply", "抱歉，我没有理解您的问题。"),
            "suggestions": response.get("suggestions", [])
        }
    except Exception as e:
        logger.error(f"AI聊天错误: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"AI聊天错误: {str(e)}"
        }

async def ai_error_feedback(request: Request):
    """AI错误反馈功能"""
    # 检查模块是否可用
    if not IDE_MODULE_AVAILABLE:
        return {
            "status": "error",
            "message": "IDE模块不可用"
        }
        
    try:
        # 从请求获取JSON数据
        data = await request.json()
        code = data.get("code", {})
        error_info = data.get("error_info", {})
        session_id = data.get("session_id", "")
        
        # 获取AI服务实例
        ai_service = get_ai_service()
        
        # 获取学生模型服务
        student_model_service = get_student_model_service()
        
        # 获取学生模型
        student_model = student_model_service.get_model(session_id)
        model_summary = student_model_service.get_model_summary(session_id)
        
        # 准备代码上下文
        code_context = {
            "html": code.get("html", ""),
            "css": code.get("css", ""),
            "js": code.get("js", "")
        }
        
        # 获取错误反馈
        feedback = await ai_service.get_error_feedback(
            student_model_summary=model_summary,
            code_context=code_context,
            error_info=error_info
        )
        
        return {
            "status": "success",
            "feedback": feedback.get("feedback", "抱歉，我无法提供错误反馈。"),
            "suggestions": feedback.get("suggestions", [])
        }
    except Exception as e:
        logger.error(f"AI错误反馈错误: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"AI错误反馈错误: {str(e)}"
        }

async def update_student_model(request: Request):
    """更新学生模型"""
    # 检查模块是否可用
    if not IDE_MODULE_AVAILABLE:
        return {
            "status": "error",
            "message": "IDE模块不可用"
        }
        
    try:
        # 从请求获取JSON数据
        data = await request.json()
        behavior_data = data.get("behavior_data", {})
        session_id = data.get("session_id", "")
        
        # 获取学生模型服务
        student_model_service = get_student_model_service()
        
        # 更新学生模型
        student_model_service.update_from_behavior(
            session_id=session_id,
            behavior_data=behavior_data
        )
        
        # 获取更新后的模型摘要
        model_summary = student_model_service.get_model_summary(session_id)
        
        return {
            "status": "success",
            "message": "学生模型更新成功",
            "student_model": model_summary
        }
    except Exception as e:
        logger.error(f"更新学生模型错误: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"更新学生模型错误: {str(e)}"
        }

async def get_student_model(request: Request):
    """获取学生模型"""
    # 检查模块是否可用
    if not IDE_MODULE_AVAILABLE:
        return {
            "status": "error",
            "message": "IDE模块不可用"
        }
        
    try:
        # 从路径参数获取session_id
        session_id = request.path_params.get("session_id", "")
        
        # 获取学生模型服务
        student_model_service = get_student_model_service()
        
        # 获取模型摘要
        model_summary = student_model_service.get_model_summary(session_id)
        
        return {
            "status": "success",
            "student_model": model_summary
        }
    except Exception as e:
        logger.error(f"获取学生模型错误: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"获取学生模型错误: {str(e)}"
        }

async def execute_code(code: CodeSubmission):
    """
    执行代码
    
    Args:
        code: 代码提交对象
        
    Returns:
        执行结果
    """
    if not IDE_MODULE_AVAILABLE or not code_executor:
        return {"status": "error", "message": "IDE模块不可用"}
    
    try:
        result = await code_executor.execute(code)
        return result.dict()
    except Exception as e:
        logger.error(f"代码执行错误: {str(e)}")
        return {"status": "error", "message": f"代码执行错误: {str(e)}"}

async def static_check(code: CodeSubmission):
    """
    静态检查代码
    
    Args:
        code: 代码提交对象
        
    Returns:
        检查结果
    """
    if not IDE_MODULE_AVAILABLE or not code_executor:
        return {"status": "error", "message": "IDE模块不可用"}
    
    try:
        result = await code_executor.static_check(code)
        return result
    except Exception as e:
        logger.error(f"静态检查错误: {str(e)}")
        return {"status": "error", "message": f"静态检查错误: {str(e)}"}

async def list_containers():
    """列出活动会话"""
    # 在Python方案中，这实际上是列出活动会话
    return {"status": "success", "message": "Python方案中无容器列表"}

async def cleanup_session(session_id: str):
    """
    清理会话
    
    Args:
        session_id: 会话ID
        
    Returns:
        清理结果
    """
    if not IDE_MODULE_AVAILABLE or not code_executor:
        return {"status": "error", "message": "IDE模块不可用"}
    
    try:
        success = await code_executor.cleanup_session(session_id)
        if success:
            return {"status": "success", "message": f"会话 {session_id} 清理成功"}
        else:
            return {"status": "error", "message": f"会话 {session_id} 清理失败"}
    except Exception as e:
        logger.error(f"会话清理错误: {str(e)}")
        return {"status": "error", "message": f"会话清理错误: {str(e)}"}

async def get_handler() -> Dict[str, Any]:
    """
    处理对模块API端点的GET请求。
    
    返回:
        包含模块数据的字典
    """
    logger.info("IDE 模块GET处理程序被调用")
    
    # 返回模块的基本信息
    return {
        "module": "ide_module",
        "status": "active",
        "data": {
            "name": "AI Code IDE",
            "description": "集成的代码编辑器模块，支持HTML、CSS、JavaScript编辑和实时预览"
        }
    }

async def post_handler(request: Request) -> Dict[str, Any]:
    """
    处理对模块API端点的POST请求。
    
    参数:
        request: 包含客户端数据的FastAPI请求对象
        
    返回:
        包含响应数据的字典
    """
    logger.info("IDE 模块POST处理程序被调用")
    
    # 从请求获取JSON数据
    data = await request.json()
    
    # 处理数据并返回响应
    action = data.get("action", "")
    
    if action == "getCode":
        # 获取代码的处理逻辑
        return {
            "module": "ide_module",
            "status": "success",
            "action": "getCode",
            "response": {
                "message": "获取代码功能需要通过专门的API端点实现"
            }
        }
    elif action == "setCode":
        # 设置代码的处理逻辑
        return {
            "module": "ide_module",
            "status": "success",
            "action": "setCode",
            "response": {
                "message": "设置代码功能需要通过专门的API端点实现"
            }
        }
    elif action == "executeCode":
        # 执行代码的处理逻辑
        return {
            "module": "ide_module",
            "status": "success",
            "action": "executeCode",
            "response": {
                "message": "代码执行功能需要通过专门的API端点实现"
            }
        }
    else:
        # 默认响应
        return {
            "module": "ide_module",
            "status": "success",
            "received_data": data,
            "response": {
                "message": "IDE模块接收到请求，但未指定具体操作"
            }
        }

# 向应用程序注册此模块
register_module("ide_module", get_handler, post_handler)

# 为API路由器导出处理函数
__all__ = [
    "ai_chat",
    "ai_error_feedback", 
    "update_student_model",
    "get_student_model",
    "execute_code",
    "static_check",
    "list_containers",
    "cleanup_session"
]