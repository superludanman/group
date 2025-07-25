from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
import os
import logging
import asyncio
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import signal
import sys
# Removed dotenv import as we're using environment variables from the main app
# from dotenv import load_dotenv

# Using environment variables from the main app instead of loading .env file
# load_dotenv()

# 尝试相对导入（用于主应用），如果失败则使用绝对导入（用于Docker容器）
try:
    # 导入Docker容器管理和代码执行服务
    from .docker_manager import get_docker_manager
    from .code_executor import get_code_executor, CodeSubmission

    # 导入AI功能相关模块
    from .student_model import get_student_model_service
    from .prompt_generator import get_prompt_generator
    from .ai_service import get_ai_service
except ImportError:
    # 导入Docker容器管理和代码执行服务
    from docker_manager import get_docker_manager
    from code_executor import get_code_executor, CodeSubmission

    # 导入AI功能相关模块
    from student_model import get_student_model_service
    from prompt_generator import get_prompt_generator
    from ai_service import get_ai_service

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("API")

app = FastAPI(title="IDE Module Backend")

# 启用CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应更改为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AIMessage(BaseModel):
    """AI聊天消息模型"""
    message: str
    code: Optional[Dict[str, str]] = None
    session_id: Optional[str] = None


class CodeError(BaseModel):
    """代码错误模型"""
    code: Dict[str, str]
    error_info: Dict[str, Any]
    session_id: Optional[str] = None


class BehaviorData(BaseModel):
    """用户行为数据模型"""
    session_id: str
    data: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """应用启动时执行的操作"""
    logger.info("Starting IDE Module Backend")
    
    # 初始化Docker管理器和代码执行服务
    try:
        get_docker_manager()
        get_code_executor()
        
        # 初始化AI服务相关组件
        get_student_model_service()
        get_prompt_generator()
        get_ai_service()
        
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        # 在严重错误情况下可能需要退出应用
        # sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的操作"""
    logger.info("Shutting down IDE Module Backend")
    
    # 关闭代码执行服务和Docker管理器
    try:
        code_executor = get_code_executor()
        await code_executor.shutdown()
        
        # 关闭AI服务
        ai_service = get_ai_service()
        await ai_service.close()
        
        logger.info("Services shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down services: {str(e)}")


@app.get("/")
async def read_root():
    """健康检查端点"""
    return {"status": "active", "message": "IDE Module Backend is running"}


@app.get("/containers")
async def list_containers():
    """列出所有活动容器"""
    try:
        docker_manager = get_docker_manager()
        containers = docker_manager.list_containers()
        return {"status": "success", "containers": containers}
    except Exception as e:
        logger.error(f"Error listing containers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute")
async def execute_code(code: CodeSubmission):
    """
    在沙箱环境中执行代码并返回结果
    """
    try:
        code_executor = get_code_executor()
        result = await code_executor.execute(code)
        return result.dict()
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/static-check")
async def static_check(code: CodeSubmission):
    """
    对代码进行静态检查
    """
    try:
        code_executor = get_code_executor()
        result = await code_executor.static_check(code)
        return result
    except Exception as e:
        logger.error(f"Error performing static check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/chat")
async def ai_chat(message: AIMessage):
    """
    与AI助手聊天的接口
    """
    try:
        # 获取必要的服务
        student_model_service = get_student_model_service()
        ai_service = get_ai_service()
        
        # 生成或获取会话ID
        session_id = message.session_id or "default_session"
        
        # 获取学习者模型摘要
        student_model = student_model_service.get_model(session_id)
        model_summary = student_model_service.get_model_summary(session_id)
        
        # 获取AI响应
        response = await ai_service.get_ai_response(
            student_model_summary=model_summary,
            user_message=message.message,
            code_context=message.code
        )
        
        return response
    except Exception as e:
        logger.error(f"Error in AI chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/error-feedback")
async def ai_error_feedback(error_data: CodeError):
    """
    获取AI对代码错误的反馈
    """
    try:
        # 获取必要的服务
        student_model_service = get_student_model_service()
        ai_service = get_ai_service()
        
        # 生成或获取会话ID
        session_id = error_data.session_id or "default_session"
        
        # 获取学习者模型摘要
        student_model = student_model_service.get_model(session_id)
        model_summary = student_model_service.get_model_summary(session_id)
        
        # 获取AI错误反馈
        response = await ai_service.get_error_feedback(
            student_model_summary=model_summary,
            code_context=error_data.code,
            error_info=error_data.error_info
        )
        
        return response
    except Exception as e:
        logger.error(f"Error in AI error feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/student/update")
async def update_student_model(behavior_data: BehaviorData):
    """
    更新学习者模型
    """
    try:
        # 获取学习者模型服务
        student_model_service = get_student_model_service()
        
        # 更新学习者模型
        student_model_service.update_from_behavior(
            student_id=behavior_data.session_id,
            behavior_data=behavior_data.data
        )
        
        return {"status": "success", "message": f"Student model updated for session {behavior_data.session_id}"}
    except Exception as e:
        logger.error(f"Error updating student model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/student/{session_id}")
async def get_student_model(session_id: str):
    """
    获取学习者模型摘要
    """
    try:
        # 获取学习者模型服务
        student_model_service = get_student_model_service()
        
        # 获取学习者模型摘要
        model_summary = student_model_service.get_model_summary(session_id)
        
        return {"status": "success", "student_model": model_summary}
    except Exception as e:
        logger.error(f"Error getting student model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    """
    清理会话相关资源
    """
    try:
        code_executor = get_code_executor()
        success = await code_executor.cleanup_session(session_id)
        if success:
            return {"status": "success", "message": f"Session {session_id} cleaned up"}
        else:
            return {"status": "error", "message": f"Failed to clean up session {session_id}"}
    except Exception as e:
        logger.error(f"Error cleaning up session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# 设置信号处理，确保优雅关闭
def signal_handler(sig, frame):
    """处理终止信号"""
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    # 获取配置
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("IDE_MODULE_PORT", "8080"))
    reload = os.environ.get("RELOAD", "False").lower() in ("true", "1", "t")
    
    # 启动服务器
    uvicorn.run("app:app", host=host, port=port, reload=reload)