import logging
import time
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SessionManager")

class SessionManager:
    """会话管理器，负责管理用户会话"""
    
    def __init__(self, 
                 max_sessions: int = 100,
                 session_timeout: int = 3600):
        """
        初始化会话管理器
        
        Args:
            max_sessions: 最大会话数量
            session_timeout: 会话超时时间(秒)
        """
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"SessionManager initialized with max sessions: {max_sessions}")
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        创建新的会话或获取现有会话
        
        Args:
            session_id: 会话ID，如果未提供则自动生成
            
        Returns:
            会话ID
        """
        # 清理过期会话
        self.cleanup_expired_sessions()
        
        # 生成会话ID（如果没有提供）
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")
        else:
            logger.info(f"Using provided session ID: {session_id}")
        
        # 检查会话是否已存在
        if session_id in self.active_sessions:
            logger.info(f"Session ID already exists: {session_id}, reusing directly")
            self.active_sessions[session_id]["last_used"] = datetime.now()
            return session_id
        
        # 检查是否达到最大会话数量
        if len(self.active_sessions) >= self.max_sessions:
            logger.warning(f"Maximum session limit reached: {self.max_sessions}")
            raise Exception("Maximum session limit reached")
        
        try:
            logger.info(f"Creating session: {session_id}")
            
            # 记录会话信息
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now(),
                "last_used": datetime.now()
            }
            
            logger.info(f"Session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定ID的会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话对象，如果不存在则返回None
        """
        if session_id in self.active_sessions:
            # 更新最后使用时间
            self.active_sessions[session_id]["last_used"] = datetime.now()
            return self.active_sessions[session_id]
        return None
        
    def find_session_by_id(self, session_id: str) -> Optional[str]:
        """
        通过会话ID查找会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话ID，如果不存在则返回None
        """
        if session_id in self.active_sessions:
            # 更新最后使用时间
            self.active_sessions[session_id]["last_used"] = datetime.now()
            return session_id
        return None
    
    def stop_session(self, session_id: str) -> bool:
        """
        停止并移除指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            操作是否成功
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session not found for stopping: {session_id}")
            return False
        
        try:
            logger.info(f"Stopping session: {session_id}")
            
            # 从活动会话列表中移除
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                
            return True
        except Exception as e:
            logger.error(f"Error stopping session: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期的会话
        
        Returns:
            清理的会话数量
        """
        now = datetime.now()
        expired_sessions = []
        
        # 查找过期会话
        for session_id, info in self.active_sessions.items():
            last_used = info.get("last_used", info.get("created_at"))
            if now - last_used > timedelta(seconds=self.session_timeout):
                expired_sessions.append(session_id)
        
        # 停止过期会话
        count = 0
        for session_id in expired_sessions:
            if self.stop_session(session_id):
                count += 1
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")
        
        return count
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        列出所有活动会话
        
        Returns:
            会话信息列表
        """
        result = []
        for session_id, info in self.active_sessions.items():
            result.append({
                "id": session_id,
                "session_id": info["session_id"],
                "created_at": info["created_at"].isoformat(),
                "last_used": info["last_used"].isoformat(),
                "age_seconds": (datetime.now() - info["created_at"]).total_seconds()
            })
        return result
    
    def shutdown(self) -> None:
        """关闭所有会话并清理资源"""
        logger.info("Shutting down SessionManager...")
        
        # 清理所有会话
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            self.stop_session(session_id)
        
        logger.info("SessionManager shutdown complete")

# 单例模式
_session_manager_instance = None

def get_session_manager() -> SessionManager:
    """获取SessionManager单例"""
    global _session_manager_instance
    if _session_manager_instance is None:
        # 从环境变量获取配置
        max_sessions = int(os.environ.get("MAX_SESSIONS", "100"))
        session_timeout = int(os.environ.get("SESSION_TIMEOUT", "3600"))
        
        _session_manager_instance = SessionManager(
            max_sessions=max_sessions,
            session_timeout=session_timeout
        )
    return _session_manager_instance