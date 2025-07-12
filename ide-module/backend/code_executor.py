import logging
import asyncio
import time
import os
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from docker_manager import get_docker_manager

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
        self.docker_manager = get_docker_manager()
        logger.info("CodeExecutor initialized")
    
    async def execute(self, code: CodeSubmission) -> ExecutionResult:
        """
        执行代码
        
        Args:
            code: 代码提交对象
            
        Returns:
            执行结果
        """
        try:
            # 获取或创建容器
            container_id = await self._get_or_create_container(code.session_id)
            
            # 执行代码
            result = await self._run_code_in_container(container_id, code)
            
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
            # 获取或创建容器
            container_id = await self._get_or_create_container(code.session_id)
            
            # 执行静态检查
            result = await self._run_static_check(container_id, code)
            
            return result
        except Exception as e:
            logger.error(f"Error performing static check: {str(e)}")
            return {
                "status": "error",
                "message": "Error performing static check",
                "details": str(e)
            }
    
    async def _get_or_create_container(self, session_id: Optional[str] = None) -> str:
        """
        获取或创建Docker容器
        
        Args:
            session_id: 会话ID
            
        Returns:
            容器ID
        """
        # 使用线程池执行阻塞的Docker操作
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.docker_manager.create_container, session_id)
    
    async def _run_code_in_container(self, container_id: str, code: CodeSubmission) -> ExecutionResult:
        """
        在容器中运行代码
        
        Args:
            container_id: 容器ID
            code: 代码提交对象
            
        Returns:
            执行结果
        """
        # 使用线程池执行阻塞的Docker操作
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self.docker_manager.execute_code,
            container_id,
            code.html,
            code.css,
            code.js
        )
        
        if result.get("status") == "success":
            return ExecutionResult(
                status="success",
                container_id=result.get("container_id"),
                preview_url=result.get("preview_url"),
                local_url=result.get("local_url")
            )
        else:
            return ExecutionResult(
                status="error",
                message=result.get("message", "Unknown error"),
                details=result.get("details")
            )
    
    async def _run_static_check(self, container_id: str, code: CodeSubmission) -> Dict[str, Any]:
        """
        在容器中运行静态检查
        
        Args:
            container_id: 容器ID
            code: 代码提交对象
            
        Returns:
            检查结果
        """
        # 这里可以实现代码静态检查
        # 为简化示例，返回模拟结果
        return {
            "status": "success",
            "errors": [],
            "warnings": [
                {"line": 5, "column": 10, "message": "示例警告：未闭合的标签", "severity": "warning"}
            ]
        }
    
    async def cleanup_session(self, session_id: str) -> bool:
        """
        清理会话相关资源
        
        Args:
            session_id: 会话ID
            
        Returns:
            操作是否成功
        """
        # 实际实现中应查找并停止与会话关联的容器
        # 简化示例中直接返回成功
        return True
    
    async def shutdown(self) -> None:
        """关闭服务并清理资源"""
        logger.info("Shutting down CodeExecutor...")
        
        # 使用线程池执行阻塞的Docker操作
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.docker_manager.shutdown)
        
        logger.info("CodeExecutor shutdown complete")


# 单例模式
_code_executor_instance = None

def get_code_executor() -> CodeExecutor:
    """获取CodeExecutor单例"""
    global _code_executor_instance
    if _code_executor_instance is None:
        _code_executor_instance = CodeExecutor()
    return _code_executor_instance