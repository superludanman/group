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

# 导入AI功能相关模块
from student_model import get_student_model_service
from prompt_generator import get_prompt_generator
from ai_service import get_ai_service

# 导入改进的分析模块
try:
    from analytics.api_integration import (
        get_api_integration_service, 
        BehaviorLogRequest, 
        QuizGenerationRequest, 
        QuizEvaluationRequest,
        PerformanceUpdateRequest
    )
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"分析模块导入失败: {e}")
    ANALYTICS_AVAILABLE = False

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
        
        # 初始化改进的分析服务
        if ANALYTICS_AVAILABLE:
            get_api_integration_service()
            logger.info("Enhanced analytics services initialized")
        
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


# ============================================================================
# 新增的 v2 API 路由 - 改进的学习者模型和自动出题系统
# ============================================================================

@app.get("/api/v2/student-model/{student_id}")
async def get_student_model_v2(student_id: str):
    """获取改进的学习者模型摘要"""
    if not ANALYTICS_AVAILABLE:
        raise HTTPException(status_code=503, detail="分析服务不可用")
    
    try:
        api_integration = get_api_integration_service()
        return await api_integration.get_student_model_summary(student_id)
    except Exception as e:
        logger.error(f"Error getting student model v2: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/behavior/log")
async def log_behavior_event_v2(request: BehaviorLogRequest):
    """记录用户行为数据"""
    if not ANALYTICS_AVAILABLE:
        raise HTTPException(status_code=503, detail="分析服务不可用")
    
    try:
        api_integration = get_api_integration_service()
        return await api_integration.log_behavior_event(request)
    except Exception as e:
        logger.error(f"Error logging behavior event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/quiz/generate")
async def generate_adaptive_quiz_v2(request: QuizGenerationRequest):
    """生成自适应测试题"""
    if not ANALYTICS_AVAILABLE:
        raise HTTPException(status_code=503, detail="分析服务不可用")
    
    try:
        api_integration = get_api_integration_service()
        return await api_integration.generate_adaptive_quiz(request)
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/quiz/evaluate")
async def evaluate_quiz_answers_v2(request: QuizEvaluationRequest):
    """评估测试答案"""
    if not ANALYTICS_AVAILABLE:
        raise HTTPException(status_code=503, detail="分析服务不可用")
    
    try:
        api_integration = get_api_integration_service()
        return await api_integration.evaluate_quiz_answers(request)
    except Exception as e:
        logger.error(f"Error evaluating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/performance/update")
async def update_performance_v2(request: PerformanceUpdateRequest):
    """更新学习表现"""
    if not ANALYTICS_AVAILABLE:
        raise HTTPException(status_code=503, detail="分析服务不可用")
    
    try:
        api_integration = get_api_integration_service()
        return await api_integration.update_performance(request)
    except Exception as e:
        logger.error(f"Error updating performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/learning/progress/{student_id}")
async def get_learning_progress_v2(student_id: str):
    """获取学习进度分析"""
    if not ANALYTICS_AVAILABLE:
        raise HTTPException(status_code=503, detail="分析服务不可用")
    
    try:
        api_integration = get_api_integration_service()
        return await api_integration.get_learning_progress(student_id)
    except Exception as e:
        logger.error(f"Error getting learning progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/info")
async def get_api_v2_info():
    """获取v2 API信息和功能"""
    return {
        "version": "2.0",
        "description": "改进的学习者模型和自动出题系统",
        "features": [
            "实时行为数据采集",
            "多维度状态推理",
            "自适应测试题生成", 
            "智能答案评估",
            "个性化学习建议",
            "时间衰减知识模型",
            "贝叶斯知识追踪"
        ],
        "endpoints": {
            "student_model": "/api/v2/student-model/{student_id}",
            "behavior_logging": "/api/v2/behavior/log",
            "quiz_generation": "/api/v2/quiz/generate",
            "quiz_evaluation": "/api/v2/quiz/evaluate",
            "performance_update": "/api/v2/performance/update",
            "learning_progress": "/api/v2/learning/progress/{student_id}"
        },
        "analytics_available": ANALYTICS_AVAILABLE
    }


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