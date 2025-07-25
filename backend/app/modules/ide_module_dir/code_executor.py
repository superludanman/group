import logging
import asyncio
import time
import os
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

# 导入新的静态检查器和预览服务器
from .static_checker import get_static_checker
from .preview_server import get_preview_server

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CodeExecutor")

class CodeSubmission(BaseModel):
    """代码提交模型"""
    html: str
    css: Optional[str] = ""
    js: Optional[str] = ""
    session_id: Optional[str] = None

class ExecutionResult(BaseModel):
    """执行结果模型"""
    status: str
    container_id: Optional[str] = None
    preview_url: Optional[str] = None
    local_url: Optional[str] = None
    message: Optional[str] = None
    details: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None

class CodeExecutor:
    """代码执行服务"""
    
    def __init__(self):
        """初始化代码执行服务"""
        self.static_checker = get_static_checker()
        self.preview_server = get_preview_server()
        logger.info("CodeExecutor initialized with Python implementation")
    
    async def execute(self, code: CodeSubmission) -> ExecutionResult:
        """
        执行代码
        
        Args:
            code: 代码提交对象
            
        Returns:
            执行结果
        """
        try:
            logger.info(f"Executing code for session: {code.session_id}")
            
            # 执行代码预览
            result = await self._run_code_preview(code)
            
            return result
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}")
            return ExecutionResult(
                status="error",
                message="Error executing code",
                details=str(e)
            )
    
    async def static_check(self, code: CodeSubmission) -> Dict[str, Any]:
        """
        对代码进行静态检查
        
        Args:
            code: 代码提交对象
            
        Returns:
            检查结果
        """
        try:
            logger.info(f"Performing static check for session: {code.session_id}")
            
            # 执行静态检查
            result = await self._run_static_check(code)
            
            return result
        except Exception as e:
            logger.error(f"Error performing static check: {str(e)}")
            return {
                "status": "error",
                "message": "Error performing static check",
                "details": str(e)
            }
    
    async def _run_code_preview(self, code: CodeSubmission) -> ExecutionResult:
        """
        运行代码预览
        
        Args:
            code: 代码提交对象
            
        Returns:
            执行结果
        """
        try:
            # 创建预览
            preview_result = self.preview_server.create_preview(
                html_code=code.html,
                css_code=code.css,
                js_code=code.js,
                session_id=code.session_id
            )
            
            if preview_result.get("status") == "success":
                return ExecutionResult(
                    status="success",
                    container_id=preview_result.get("session_id"),
                    preview_url=preview_result.get("preview_url"),
                    local_url=preview_result.get("preview_url")
                )
            else:
                return ExecutionResult(
                    status="error",
                    message=preview_result.get("message", "Unknown error"),
                    details=preview_result.get("details")
                )
        except Exception as e:
            logger.error(f"Error in _run_code_preview: {str(e)}")
            raise
    
    async def _run_static_check(self, code: CodeSubmission) -> Dict[str, Any]:
        """
        运行静态检查
        
        Args:
            code: 代码提交对象
            
        Returns:
            检查结果
        """
        try:
            # 使用静态检查器检查所有代码
            result = self.static_checker.check_all(
                html_code=code.html,
                css_code=code.css,
                js_code=code.js
            )
            
            return result
        except Exception as e:
            logger.error(f"Error in _run_static_check: {str(e)}")
            raise
    
    async def cleanup_session(self, session_id: str) -> bool:
        """
        清理会话相关资源
        
        Args:
            session_id: 会话ID
            
        Returns:
            操作是否成功
        """
        try:
            # 清理预览服务器中的会话
            success = self.preview_server.cleanup_session(session_id)
            if success:
                logger.info(f"Successfully cleaned up session: {session_id}")
                return True
            else:
                logger.warning(f"Failed to clean up session: {session_id}")
                return False
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """关闭服务并清理资源"""
        logger.info("Shutting down CodeExecutor...")
        
        # 停止预览服务器
        self.preview_server.stop()
        
        logger.info("CodeExecutor shutdown complete")

# 单例模式
_code_executor_instance = None

def get_code_executor() -> CodeExecutor:
    """获取CodeExecutor单例"""
    global _code_executor_instance
    if _code_executor_instance is None:
        _code_executor_instance = CodeExecutor()
    return _code_executor_instance