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
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入Docker容器管理和代码执行服务
from docker_manager import get_docker_manager
from code_executor import get_code_executor, CodeSubmission

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
    code: Optional[str] = None
    session_id: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """应用启动时执行的操作"""
    logger.info("Starting IDE Module Backend")
    
    # 初始化Docker管理器和代码执行服务
    try:
        get_docker_manager()
        get_code_executor()
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
    与AI助手聊天的接口 (占位，需要后续集成实际的AI API)
    """
    try:
        # 此处为占位实现，后续需集成到实际的AI API
        return {
            "status": "success",
            "reply": "这是一个AI助手回复的占位文本。请在后续开发中集成实际的AI API。",
            "suggestions": ["尝试修复HTML结构", "检查CSS语法", "添加事件监听器"]
        }
    except Exception as e:
        logger.error(f"Error in AI chat: {str(e)}")
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
    port = int(os.environ.get("PORT", "8080"))
    reload = os.environ.get("RELOAD", "False").lower() in ("true", "1", "t")
    
    # 启动服务器
    uvicorn.run("app:app", host=host, port=port, reload=reload)