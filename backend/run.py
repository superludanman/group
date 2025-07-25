"""
运行脚本

此脚本提供了启动AI HTML学习平台后端的简单方法。
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log')
    ]
)
logger = logging.getLogger("run")

def load_env():
    """手动加载环境变量文件"""
    # 优先加载根目录的.env文件
    root_env_path = Path(__file__).parent.parent / '.env'
    backend_env_path = Path(__file__).parent / '.env'
    
    logger.info(f"根目录环境变量文件路径: {root_env_path}")
    logger.info(f"根目录环境变量文件是否存在: {root_env_path.exists()}")
    logger.info(f"后端目录环境变量文件路径: {backend_env_path}")
    logger.info(f"后端目录环境变量文件是否存在: {backend_env_path.exists()}")
    
    # 优先加载根目录的.env文件
    env_path = root_env_path if root_env_path.exists() else backend_env_path
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    logger.info(f"设置环境变量: {key}={value[:10]}..." if len(value) > 10 else f"设置环境变量: {key}={value}")
    else:
        logger.warning(f"未找到环境变量文件: {env_path}")

def main():
    """启动应用程序。"""
    logger.info("启动AI HTML学习平台后端")
    
    # 加载环境变量
    load_env()
    
    # 打印环境变量信息
    logger.info(f"OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'Not set')[:20] if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
    logger.info(f"OPENAI_API_BASE: {os.environ.get('OPENAI_API_BASE', 'Not set')}")
    logger.info(f"OPENAI_MODEL: {os.environ.get('OPENAI_MODEL', 'Not set')}")
    
    # 检查是否在正确的目录中
    if not Path("app/main.py").exists():
        logger.error("错误：app/main.py未找到。确保您从项目根目录运行此脚本。")
        return False
    
    # 检查虚拟环境是否激活
    venv_activated = os.environ.get("VIRTUAL_ENV") is not None
    if not venv_activated:
        logger.warning("警告：未检测到虚拟环境。建议在虚拟环境中运行。")
    
    # 检查是否安装了要求的包
    try:
        import fastapi
    except ImportError:
        logger.error("错误：未找到所需的包。请先运行'pip install -r requirements.txt'。")
        return False
    
    # 获取端口配置，默认为8000
    # 开发者注意：请在项目根目录的.env文件中配置端口，而非修改此处硬编码
    port = int(os.environ.get("BACKEND_PORT", "8000"))
    host = "0.0.0.0"
    
    logger.info(f"启动服务器，地址为http://localhost:{port}")
    
    # 启动服务器
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)