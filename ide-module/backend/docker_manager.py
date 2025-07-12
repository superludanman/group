import docker
import logging
import time
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DockerManager")

class DockerManager:
    """Docker容器管理器，负责创建、启动、停止和监控Docker容器"""
    
    def __init__(self, 
                 base_image: str = "ide-sandbox:latest",
                 max_containers: int = 10,
                 container_timeout: int = 300,
                 network_name: str = "ide-network",
                 workspace_dir: str = "/workspace"):
        """
        初始化Docker管理器
        
        Args:
            base_image: 基础镜像名称
            max_containers: 最大容器数量
            container_timeout: 容器超时时间(秒)
            network_name: Docker网络名称
            workspace_dir: 容器内工作目录
        """
        self.client = docker.from_env()
        self.base_image = base_image
        self.max_containers = max_containers
        self.container_timeout = container_timeout
        self.network_name = network_name
        self.workspace_dir = workspace_dir
        self.active_containers: Dict[str, Dict[str, Any]] = {}
        
        # 确保网络存在
        self._ensure_network()
        
        logger.info(f"DockerManager initialized with base image: {base_image}")
    
    def _ensure_network(self) -> None:
        """确保Docker网络存在"""
        try:
            networks = self.client.networks.list(names=[self.network_name])
            if not networks:
                logger.info(f"Creating Docker network: {self.network_name}")
                self.client.networks.create(self.network_name, driver="bridge")
            else:
                logger.info(f"Docker network {self.network_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring Docker network: {str(e)}")
            raise
    
    def create_container(self, session_id: Optional[str] = None) -> str:
        """
        创建新的Docker容器
        
        Args:
            session_id: 会话ID，如果未提供则自动生成
            
        Returns:
            容器ID
        """
        # 清理过期容器
        self.cleanup_expired_containers()
        
        # 检查是否达到最大容器数量
        if len(self.active_containers) >= self.max_containers:
            logger.warning(f"Maximum container limit reached: {self.max_containers}")
            raise Exception("Maximum container limit reached")
        
        # 生成会话ID和容器名称
        if not session_id:
            session_id = str(uuid.uuid4())
        container_name = f"ide-sandbox-{session_id}"
        
        try:
            logger.info(f"Creating container: {container_name}")
            
            # 容器配置
            container = self.client.containers.run(
                image=self.base_image,
                name=container_name,
                detach=True,
                network=self.network_name,
                mem_limit="256m",
                cpu_quota=50000,  # 50% of CPU
                cpu_period=100000,
                restart_policy={"Name": "no"},
                cap_drop=["ALL"],
                security_opt=["no-new-privileges"],
                read_only=False,  # 需要写入权限以生成文件
                volumes={
                    # 可以添加特定的卷挂载
                },
                environment={
                    "SESSION_ID": session_id,
                    "CONTAINER_TIMEOUT": str(self.container_timeout)
                },
                command=["http-server", "-p", "3000"]
            )
            
            # 记录容器信息
            self.active_containers[container.id] = {
                "container": container,
                "session_id": session_id,
                "created_at": datetime.now(),
                "last_used": datetime.now(),
                "name": container_name
            }
            
            logger.info(f"Container created: {container.id} (session: {session_id})")
            return container.id
            
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            raise
    
    def get_container(self, container_id: str) -> Optional[docker.models.containers.Container]:
        """
        获取指定ID的容器
        
        Args:
            container_id: 容器ID
            
        Returns:
            容器对象，如果不存在则返回None
        """
        if container_id in self.active_containers:
            # 更新最后使用时间
            self.active_containers[container_id]["last_used"] = datetime.now()
            return self.active_containers[container_id]["container"]
        return None
    
    def execute_code(self, container_id: str, html_code: str, css_code: str, js_code: str) -> Dict[str, Any]:
        """
        在指定容器中执行代码
        
        Args:
            container_id: 容器ID
            html_code: HTML代码
            css_code: CSS代码
            js_code: JavaScript代码
            
        Returns:
            执行结果字典
        """
        container = self.get_container(container_id)
        if not container:
            logger.error(f"Container not found: {container_id}")
            raise Exception(f"Container not found: {container_id}")
        
        try:
            # 更新最后使用时间
            self.active_containers[container_id]["last_used"] = datetime.now()
            
            # 创建临时文件
            file_id = str(uuid.uuid4())
            html_file = f"index_{file_id}.html"
            
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
            
            # 写入文件到容器
            # 使用Base64编码来避免特殊字符引起的问题
            import base64
            encoded_content = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
            exec_result = container.exec_run(
                cmd=f"bash -c \"mkdir -p {self.workspace_dir}/temp && echo '{encoded_content}' | base64 -d > {self.workspace_dir}/temp/{html_file}\"",
                privileged=False
            )
            
            if exec_result.exit_code != 0:
                logger.error(f"Error writing code file: {exec_result.output.decode('utf-8')}")
                return {
                    "status": "error",
                    "message": "Failed to write code file",
                    "details": exec_result.output.decode('utf-8')
                }
            
            # 启动预览服务
            preview_url = f"http://{container.name}:3000/temp/{html_file}"
            
            return {
                "status": "success",
                "container_id": container_id,
                "file_id": file_id,
                "preview_url": preview_url,
                "local_url": f"http://localhost:3000/temp/{html_file}"
            }
            
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}")
            return {
                "status": "error",
                "message": "Error executing code",
                "details": str(e)
            }
    
    def stop_container(self, container_id: str) -> bool:
        """
        停止并移除指定容器
        
        Args:
            container_id: 容器ID
            
        Returns:
            操作是否成功
        """
        container = self.get_container(container_id)
        if not container:
            logger.warning(f"Container not found for stopping: {container_id}")
            return False
        
        try:
            logger.info(f"Stopping container: {container_id}")
            container.stop(timeout=5)
            container.remove(force=True)
            
            # 从活动容器列表中移除
            if container_id in self.active_containers:
                del self.active_containers[container_id]
                
            return True
        except Exception as e:
            logger.error(f"Error stopping container: {str(e)}")
            return False
    
    def cleanup_expired_containers(self) -> int:
        """
        清理过期的容器
        
        Returns:
            清理的容器数量
        """
        now = datetime.now()
        expired_containers = []
        
        # 查找过期容器
        for container_id, info in self.active_containers.items():
            last_used = info.get("last_used", info.get("created_at"))
            if now - last_used > timedelta(seconds=self.container_timeout):
                expired_containers.append(container_id)
        
        # 停止过期容器
        count = 0
        for container_id in expired_containers:
            if self.stop_container(container_id):
                count += 1
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired containers")
        
        return count
    
    def list_containers(self) -> List[Dict[str, Any]]:
        """
        列出所有活动容器
        
        Returns:
            容器信息列表
        """
        result = []
        for container_id, info in self.active_containers.items():
            container = info["container"]
            result.append({
                "id": container_id,
                "name": info["name"],
                "session_id": info["session_id"],
                "status": container.status,
                "created_at": info["created_at"].isoformat(),
                "last_used": info["last_used"].isoformat(),
                "age_seconds": (datetime.now() - info["created_at"]).total_seconds()
            })
        return result
    
    def shutdown(self) -> None:
        """关闭所有容器并清理资源"""
        logger.info("Shutting down DockerManager...")
        
        # 停止所有容器
        container_ids = list(self.active_containers.keys())
        for container_id in container_ids:
            self.stop_container(container_id)
        
        logger.info("DockerManager shutdown complete")


# 单例模式
_docker_manager_instance = None

def get_docker_manager() -> DockerManager:
    """获取DockerManager单例"""
    global _docker_manager_instance
    if _docker_manager_instance is None:
        # 从环境变量获取配置
        base_image = os.environ.get("SANDBOX_IMAGE", "ide-sandbox:latest")
        max_containers = int(os.environ.get("MAX_CONTAINERS", "10"))
        container_timeout = int(os.environ.get("CONTAINER_TIMEOUT", "300"))
        network_name = os.environ.get("DOCKER_NETWORK", "ide-network")
        
        _docker_manager_instance = DockerManager(
            base_image=base_image,
            max_containers=max_containers,
            container_timeout=container_timeout,
            network_name=network_name
        )
    return _docker_manager_instance