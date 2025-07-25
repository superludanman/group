"""
模块加载器

此文件提供了将模块动态加载到应用程序中的框架。
团队成员可以将他们的模块添加到modules目录并在此处注册。
"""

import importlib
import logging
import os
import sys
from typing import Dict, Any, Callable, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 存储已注册模块的字典
registered_modules: Dict[str, Dict[str, Any]] = {}

def register_module(module_name: str, get_handler: Callable, post_handler: Callable) -> bool:
    """
    向应用程序注册一个模块。
    
    参数：
        module_name: 模块名称
        get_handler: 处理对模块API端点GET请求的函数
        post_handler: 处理对模块API端点POST请求的函数
        
    返回：
        bool: 如果注册成功则为True，否则为False
    """
    if module_name in registered_modules:
        logger.warning(f"模块 {module_name} 已经注册。正在覆盖...")
    
    registered_modules[module_name] = {
        "get_handler": get_handler,
        "post_handler": post_handler
    }
    
    logger.info(f"模块 {module_name} 注册成功")
    return True

def get_module_handler(module_name: str) -> Optional[Callable]:
    """获取已注册模块的GET处理程序。"""
    if module_name not in registered_modules:
        logger.warning(f"模块 {module_name} 未注册")
        return None
    
    return registered_modules[module_name]["get_handler"]

def post_module_handler(module_name: str) -> Optional[Callable]:
    """获取已注册模块的POST处理程序。"""
    if module_name not in registered_modules:
        logger.warning(f"模块 {module_name} 未注册")
        return None
    
    return registered_modules[module_name]["post_handler"]

def load_all_modules() -> None:
    """
    动态加载模块目录中的所有模块。
    
    此函数在模块目录中搜索Python文件并尝试导入它们。
    每个模块应调用register_module()以注册自身。
    """
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, modules_dir)
    sys.path.insert(0, os.path.dirname(modules_dir))  # 添加 app 目录到路径
    
    for file in os.listdir(modules_dir):
        # 跳过目录和特殊文件
        if os.path.isdir(os.path.join(modules_dir, file)):
            continue
        if file.endswith('.py') and file != '__init__.py' and file != os.path.basename(__file__):
            module_name = file[:-3]  # 移除.py扩展名
            try:
                # 尝试使用绝对导入
                importlib.import_module(f"app.modules.{module_name}")
                logger.info(f"已加载模块文件: {module_name}")
            except Exception as e:
                logger.error(f"加载模块 {module_name} 时出错: {str(e)}")
                try:
                    # 备用方案：尝试直接导入
                    importlib.import_module(module_name)
                    logger.info(f"已加载模块文件: {module_name}")
                except Exception as e2:
                    logger.error(f"备用方案加载模块 {module_name} 时也出错: {str(e2)}")
    
    logger.info(f"已加载 {len(registered_modules)} 个模块: {list(registered_modules.keys())}")

# 示例模块模板函数
def create_module_template(module_name: str) -> None:
    """
    为团队成员创建一个模板模块文件以供实现。
    
    参数:
        module_name: 要创建的模块名称
    """
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(modules_dir, f"{module_name}.py")
    
    if os.path.exists(file_path):
        logger.warning(f"模块文件 {file_path} 已存在。不覆盖。")
        return
    
    template = f'''"""
{module_name.replace('_', ' ').title()} 模块

此模块处理 AI HTML学习平台的 {module_name.replace('_', ' ')} 功能。
"""

from typing import Dict, Any
from fastapi import Request
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 导入模块加载器
from .module_loader import register_module

async def get_handler() -> Dict[str, Any]:
    """
    处理对模块API端点的GET请求。
    
    返回:
        包含模块数据的字典
    """
    logger.info(f"{module_name} 模块GET处理程序被调用")
    
    # 在此实现您模块的GET功能
    return {{
        "module": "{module_name}",
        "status": "active",
        "data": {{
            # 在此添加您的模块数据
        }}
    }}

async def post_handler(request: Request) -> Dict[str, Any]:
    """
    处理对模块API端点的POST请求。
    
    参数:
        request: 包含客户端数据的FastAPI请求对象
        
    返回:
        包含响应数据的字典
    """
    logger.info(f"{module_name} 模块POST处理程序被调用")
    
    # 从请求获取JSON数据
    data = await request.json()
    
    # 在此实现您模块的POST功能
    # 处理数据并返回响应
    
    return {{
        "module": "{module_name}",
        "status": "success",
        "received_data": data,
        "response": {{
            # 在此添加您的响应数据
        }}
    }}

# 向应用程序注册此模块
register_module("{module_name}", get_handler, post_handler)
'''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    logger.info(f"已创建模块模板: {file_path}")

# 创建示例模块
def create_example_modules() -> None:
    """为每个主要功能创建示例模块模板。"""
    for module_name in ["preview_module", "editor_module", "sandbox_module", "summary_module"]:
        create_module_template(module_name)