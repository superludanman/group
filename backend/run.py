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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("run")

def main():
    """启动应用程序。"""
    logger.info("启动AI HTML学习平台后端")
    
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
    
    # 启动应用程序
    port = 8000
    host = "0.0.0.0"
    
    logger.info(f"启动服务器，地址为http://localhost:{port}")
    
    # 启动服务器
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)