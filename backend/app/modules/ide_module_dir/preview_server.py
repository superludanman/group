"""
本地预览服务模块
使用Python内置的HTTP服务器提供代码预览功能
"""

import http.server
import socketserver
import threading
import os
import tempfile
import logging
import uuid
import time
from typing import Dict, Any, Optional
import urllib.parse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreviewServer:
    """本地预览服务器类"""
    
    def __init__(self, port: int = 8081):
        """
        初始化预览服务器
        
        Args:
            port: 服务器端口
        """
        self.port = port
        self.server_thread: Optional[threading.Thread] = None
        self.httpd: Optional[socketserver.TCPServer] = None
        self.is_running = False
        self.temp_dir = tempfile.mkdtemp(prefix="code_preview_")
        logger.info(f"PreviewServer initialized with temp dir: {self.temp_dir}")
    
    def start(self) -> bool:
        """
        启动预览服务器
        
        Returns:
            启动是否成功
        """
        if self.is_running:
            logger.warning("Preview server is already running")
            return True
        
        try:
            # 创建HTTP请求处理器
            handler = self._create_request_handler()
            
            # 创建服务器
            self.httpd = socketserver.TCPServer(("", self.port), handler)
            
            # 在单独的线程中启动服务器
            self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            logger.info(f"Preview server started on port {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start preview server: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        停止预览服务器
        
        Returns:
            停止是否成功
        """
        if not self.is_running:
            logger.warning("Preview server is not running")
            return True
        
        try:
            if self.httpd:
                self.httpd.shutdown()
                self.httpd.server_close()
            
            if self.server_thread:
                self.server_thread.join(timeout=5)
            
            self.is_running = False
            logger.info("Preview server stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop preview server: {str(e)}")
            return False
    
    def create_preview(self, html_code: str, css_code: str = "", js_code: str = "", 
                      session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        创建代码预览
        
        Args:
            html_code: HTML代码
            css_code: CSS代码
            js_code: JavaScript代码
            session_id: 会话ID
            
        Returns:
            预览信息字典
        """
        if not self.is_running:
            logger.warning("Preview server is not running, starting it now...")
            if not self.start():
                return {
                    "status": "error",
                    "message": "Failed to start preview server"
                }
        
        try:
            # 生成会话ID（如果没有提供）
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 创建会话目录
            session_dir = os.path.join(self.temp_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # 构建完整的HTML文件
            full_html = self._build_full_html(html_code, css_code, js_code)
            
            # 生成文件名
            filename = f"preview_{int(time.time())}.html"
            filepath = os.path.join(session_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            # 生成预览URL
            preview_url = f"http://localhost:{self.port}/{session_id}/{filename}"
            
            logger.info(f"Preview created: {preview_url}")
            return {
                "status": "success",
                "session_id": session_id,
                "preview_url": preview_url,
                "filepath": filepath
            }
        except Exception as e:
            logger.error(f"Failed to create preview: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create preview: {str(e)}"
            }
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        清理会话文件
        
        Args:
            session_id: 会话ID
            
        Returns:
            清理是否成功
        """
        try:
            session_dir = os.path.join(self.temp_dir, session_id)
            if os.path.exists(session_dir):
                import shutil
                shutil.rmtree(session_dir)
                logger.info(f"Session {session_id} cleaned up")
                return True
            else:
                logger.warning(f"Session {session_id} not found")
                return True
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {str(e)}")
            return False
    
    def _build_full_html(self, html_code: str, css_code: str, js_code: str) -> str:
        """
        构建完整的HTML文件
        
        Args:
            html_code: HTML代码
            css_code: CSS代码
            js_code: JavaScript代码
            
        Returns:
            完整的HTML字符串
        """
        # 构建HTML文件内容
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Preview</title>
    <style>
    {css_code}
    </style>
</head>
<body>
    {html_code}
    <script>
    try {{
        {js_code}
    }} catch (error) {{
        console.error('JavaScript error:', error);
        const errorDiv = document.createElement('div');
        errorDiv.style.position = 'fixed';
        errorDiv.style.bottom = '10px';
        errorDiv.style.left = '10px';
        errorDiv.style.right = '10px';
        errorDiv.style.padding = '10px';
        errorDiv.style.backgroundColor = '#ffebee';
        errorDiv.style.color = '#c62828';
        errorDiv.style.border = '1px solid #ef9a9a';
        errorDiv.style.borderRadius = '4px';
        errorDiv.style.zIndex = '9999';
        errorDiv.textContent = 'JavaScript error: ' + error.message;
        document.body.appendChild(errorDiv);
    }}
    </script>
</body>
</html>
        """
        return html_content
    
    def _create_request_handler(self):
        """
        创建HTTP请求处理器
        
        Returns:
            自定义的HTTP请求处理器类
        """
        temp_dir = self.temp_dir
        
        class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=temp_dir, **kwargs)
            
            def log_message(self, format, *args):
                # 减少日志输出
                pass
        
        return CustomHTTPRequestHandler
    
    def __del__(self):
        """析构函数，清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info(f"Temporary directory cleaned up: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup temporary directory: {str(e)}")

# 单例模式
_preview_server_instance = None

def get_preview_server() -> PreviewServer:
    """获取PreviewServer单例"""
    global _preview_server_instance
    if _preview_server_instance is None:
        _preview_server_instance = PreviewServer()
    return _preview_server_instance