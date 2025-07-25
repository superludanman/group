"""
知识图谱数据加载器

此文件用于获取知识点和用户已学习知识点数据
"""
from typing import Dict, Any
from fastapi import Request
import logging
import json
import os

# 配置日志
logger = logging.getLogger(__name__)

# 导入模块加载器
from .module_loader import register_module

# 获取当前文件的目录：A/c/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 构造指向 A/b/graph_data.json 的路径
GRAPH_DATA_PATH = os.path.join(BASE_DIR, "..", "data", "graph_data.json")

# 可选：转换成绝对路径（更安全）
GRAPH_DATA_PATH = os.path.abspath(GRAPH_DATA_PATH)
""" LEARNED_NODES_PATH = "data/learned_nodes.json" """

# 读取 JSON 文件
def read_json_file(filepath: str) -> Any:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# GET 请求处理器
async def get_handler() -> Dict[str, Any]:
    """
    处理对模块API端点的GET请求。
    
    返回:
        包含模块数据的字典
    """
    try:
        logger.info("group_loader 模块 GET 请求开始")
        graph_data = read_json_file(GRAPH_DATA_PATH)
        """  learned_nodes = read_json_file(LEARNED_NODES_PATH) """
        """ graph_data = {
                        "nodes": [
                            { "data": { "id": 'HTML', "label": 'HTML 基础' } },
                            { "data": { "id": 'CSS', "label": 'CSS 样式' } },
                            { "data": { "id": '1', "label": '1' } },
                            { "data": { "id": '2', "label": '2' } },
                            { "data": { "id": '3', "label": '3' } },
                            { "data": { "id": 'JS', "label": 'JavaScript 入门' } },
                            { "data": { "id": 'DOM', "label": 'DOM 操作' } },
                            { "data": { "id": 'AJAX', "label": 'AJAX 请求' } },
                            { "data": { "id": 'Async', "label": '异步编程' } },
                            { "data": { "id": 'Functional', "label": '函数式编程' } },
                        ],
                        "edges": [
                            { "data": { "source": 'HTML', "target": 'CSS' } },
                            { "data": { "source": 'CSS', "target": 'JS' } },
                            { "data": { "source": '1', "target": '2' } },
                            { "data": { "source": '2', "target": '3' } },
                            { "data": { "source": 'JS', "target": 'DOM' } },
                            { "data": { "source": 'DOM', "target": 'AJAX' } },
                            { "data": { "source": 'JS', "target": 'Async' } },
                            { "data": { "source": 'JS', "target": 'Functional' } },
                            { "data": { "source": 'JS', "target": 'AJAX' } },
                            { "data": { "source": 'AJAX', "target": 'JS' } },
                        ]
                    } """
        learned_nodes = ['html_base']

        if graph_data is None or learned_nodes is None:
            return {
                "module": "group_loader",
                "status": "error",
                "error": "知识图谱数据或已学习节点数据未找到"
            }

        return {
            "module": "group_loader",
            "status": "success",
            "data": {
                "nodes": graph_data.get("nodes", []),
                "edges": graph_data.get("edges", []),
                "learnedNodes": learned_nodes
            }
        }
    except Exception as e:
        logger.exception("group_loader GET 处理出错")
        return {
            "module": "group_loader",
            "status": "error",
            "error": str(e)
        }

async def post_handler(request: Request) -> Dict[str, Any]:
    """
    处理对模块API端点的POST请求。
    
    参数:
        request: 包含客户端数据的FastAPI请求对象
        
    返回:
        包含响应数据的字典
    """
    logger.info("我的功能模块POST处理程序被调用")
    
    # 从请求获取JSON数据
    data = await request.json()
    
    # 在此实现您模块的POST功能
    # 处理数据并返回响应
    
    return {
        "module": "group_loader",
        "status": "error",
        "error": "该模块不支持 POST 操作"
    }

# 向应用程序注册此模块
register_module("group_loader", get_handler, post_handler)