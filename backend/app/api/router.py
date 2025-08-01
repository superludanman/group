"""
API路由模块
包含所有API端点的路由定义
"""

from fastapi import APIRouter, Request, Depends
import logging
import os

# 导入模块处理程序
from app.modules.module_loader import (
    get_module_handler,
    post_module_handler
)
from app.core.models import UserKnowledge
from app.core.config import get_db
from app.core.knowledge_map import knowledge_map
from sqlalchemy.orm import Session
from fastapi import HTTPException


# 尝试导入情绪识别模块
try:
    from app.core.EmotionModel import EmotionModel
    EMOTION_MODEL_AVAILABLE = True
except Exception as e:
    logging.warning(f"情绪识别模型未正确加载，请检查模型文件和依赖: {e}")
    EMOTION_MODEL_AVAILABLE = False


# 导入IDE模块的额外处理程序
try:
    from app.modules.ide_module import (
        ai_chat,
        ai_error_feedback,
        update_student_model,
        get_student_model,
        execute_code,
        static_check,
        list_containers,
        cleanup_session
    )
    from app.modules.ide_module_dir.code_executor import CodeSubmission
    IDE_MODULE_AVAILABLE = True
except ImportError as e:
    IDE_MODULE_AVAILABLE = False
    logging.warning(f"IDE模块后端组件未找到，代码执行功能将不可用: {e}")

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

@api_router.get("/env")
async def get_env_vars():
    """
    获取环境变量配置
    """
    env_vars = {}
    # 只返回特定的环境变量，避免暴露敏感信息
    allowed_vars = [
        "BACKEND_PORT",
        "IDE_MODULE_PORT", 
        "FRONTEND_PORT",
        "PREVIEW_PORT",
        "OPENAI_API_BASE",
        "OPENAI_MODEL",
        "OPENAI_MAX_TOKENS",
        "OPENAI_TEMPERATURE"
    ]
    
    for var in allowed_vars:
        value = os.environ.get(var)
        if value is not None:
            # 对于端口变量，转换为整数
            if var.endswith("_PORT"):
                try:
                    env_vars[var] = int(value)
                except ValueError:
                    env_vars[var] = value
            else:
                env_vars[var] = value
    
    return env_vars

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

# 保留 `feature/add-ide-intergration` 分支添加的 IDE 模块特定 API 端点
if IDE_MODULE_AVAILABLE:
    @api_router.post("/module/ide/ai/chat")
    async def ide_ai_chat(request: Request):
        """
        IDE模块AI聊天端点
        """
        return await ai_chat(request)

    @api_router.post("/module/ide/ai/error-feedback")
    async def ide_ai_error_feedback(request: Request):
        """
        IDE模块AI错误反馈端点
        """
        return await ai_error_feedback(request)

    @api_router.post("/module/ide/student/update")
    async def ide_student_update(request: Request):
        """
        IDE模块学生模型更新端点
        """
        return await update_student_model(request)

    @api_router.get("/module/ide/student/{session_id}")
    async def ide_get_student_model(session_id: str, request: Request):
        """
        IDE模块获取学生模型端点
        """
        # 为处理程序添加路径参数
        request.path_params = {"session_id": session_id}
        return await get_student_model(request)

    @api_router.get("/module/ide/containers")
    async def ide_list_containers():
        """
        IDE模块列出容器端点
        """
        return await list_containers()

    @api_router.post("/module/ide/execute")
    async def ide_execute_code(request: Request):
        """
        IDE模块代码执行端点
        """
        code_data = await request.json()
        code_submission = CodeSubmission(**code_data)
        return await execute_code(code_submission)

    @api_router.post("/module/ide/static-check")
    async def ide_static_check(request: Request):
        """
        IDE模块静态检查端点
        """
        code_data = await request.json()
        code_submission = CodeSubmission(**code_data)
        return await static_check(code_submission)

    @api_router.post("/module/ide/cleanup/{session_id}")
    async def ide_cleanup_session(session_id: str):
        """
        IDE模块清理会话端点
        """
        return await cleanup_session(session_id)
        
    # 为了兼容前端代码中的路径，添加别名路由
    @api_router.post("/ide/execute")
    async def ide_execute_code_alias(request: Request):
        """
        IDE模块代码执行端点（别名）
        """
        code_data = await request.json()
        code_submission = CodeSubmission(**code_data)
        return await execute_code(code_submission)

    @api_router.post("/ide/static-check")
    async def ide_static_check_alias(request: Request):
        """
        IDE模块静态检查端点（别名）
        """
        code_data = await request.json()
        code_submission = CodeSubmission(**code_data)
        return await static_check(code_submission)

    @api_router.post("/ide/cleanup/{session_id}")
    async def ide_cleanup_session_alias(session_id: str):
        """
        IDE模块清理会话端点（别名）
        """
        return await cleanup_session(session_id)
        
    @api_router.get("/ide/containers")
    async def ide_list_containers_alias():
        """
        IDE模块列出容器端点（别名）
        """
        return await list_containers()

# 保留 `main` 分支添加的用户知识和情绪分析 API 端点
@api_router.post("/users/{user_id}/knowledge")
async def learn_knowledge(user_id: str, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    knowledge_id = data["knowledge_id"]
    try:
        exists = db.query(UserKnowledge).filter_by(user_id=user_id, knowledge_id=knowledge_id).first()
        if not exists:
            record = UserKnowledge(user_id=user_id, knowledge_id=knowledge_id)
            db.add(record)
            db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/users/{user_id}/allowed-tags")
async def get_allowed_tags(user_id: str, db: Session = Depends(get_db)):
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/emotion")
async def emotion(request: Request):
    """
    情绪分析API端点
    """
    if not EMOTION_MODEL_AVAILABLE:
        return {
            "emotion": "未知",
            "state": "error",
            "message": "情绪识别模型不可用，请检查模型文件和依赖"
        }

    response = await request.json()
    text = response["text"]
    return await EmotionModel(text)
