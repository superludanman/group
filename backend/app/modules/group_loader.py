"""
知识图谱数据加载器

此文件用于获取知识点和用户已学习知识点数据
"""
from typing import Dict, Any
from fastapi import Request, Depends
from sqlalchemy.orm import Session
import logging
from app.core.config import get_db
from backend.app.core.models import Node, Edge, UserProgress

# 配置日志
logger = logging.getLogger(__name__)

# 导入模块加载器
from app.modules.module_loader import register_module

# GET 请求处理器
async def get_handler(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    处理对模块API端点的GET请求。
    
    返回:
        包含模块数据的字典
    """
    try:
        logger.info("group_loader 模块 GET 请求开始")
        graph_data = get_graph_data(db)  # 调用自定义函数从数据库读取数据
        learned_nodes = get_learned_nodes(db)  # 获取已学习节点

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
# 从数据库中获取知识图谱数据的函数
def get_graph_data(db: Session) -> Dict[str, Any]:
    """从数据库获取知识图谱数据"""
    nodes = db.query(Node).all()
    edges = db.query(Edge).all() 
    
    # 构建图数据
    graph_data = {
        "nodes": [{"data": {"id": node.id, "label": node.label}} for node in nodes],
        "edges": [{"data": {"source": edge.source_node, "target": edge.target_node}} for edge in edges]
    }
    return graph_data

# 获取已学习节点的函数
def get_learned_nodes(db: Session,user_id: str) -> list:
    """根据用户ID查询该用户已学习的节点"""
    learned_nodes = db.query(UserProgress.node_id).filter(UserProgress.user_id == user_id).all()
    return [node.node_id for node in learned_nodes]

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