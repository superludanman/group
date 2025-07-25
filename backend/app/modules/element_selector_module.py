from typing import Dict, Any, List, Optional
from fastapi import Request, APIRouter, Depends
import logging
import os
import json
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

# 导入模块加载器
from app.modules.module_loader import register_module
from app.core.knowledge_map import knowledge_map
from app.core.config import get_db
from app.core.models import UserKnowledge
from sqlalchemy.orm import Session

# 存储元素的目录
ELEMENTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../stored_elements'))
os.makedirs(ELEMENTS_DIR, exist_ok=True)

# GET 处理程序：返回所有已保存的元素信息
async def get_handler() -> Dict[str, Any]:
    try:
        elements = []
        for filename in os.listdir(ELEMENTS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(ELEMENTS_DIR, filename), 'r', encoding='utf-8') as f:
                    element_data = json.load(f)
                    element_id = filename.replace('.json', '')
                    elements.append({
                        "id": element_id,
                        **element_data
                    })
        return {
            "module": "element_selector",
            "status": "success",
            "data": elements
        }
    except Exception as e:
        logger.error(f"获取元素信息时出错: {str(e)}")
        return {
            "module": "element_selector",
            "status": "error",
            "error": str(e)
        }

# POST 处理程序：接收并保存前端传来的元素信息
async def post_handler(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        data = await request.json()
        user_id = data.get("user_id")
        element_tag = data.get("element_tag")
        if user_id and element_tag:
            try:
                learned = db.query(UserKnowledge).filter_by(user_id=user_id).all()
                allowed_tags = set()
                for rec in learned:
                    allowed_tags.update(knowledge_map.get(rec.knowledge_id, []))
                if element_tag not in allowed_tags:
                    return {
                        "module": "element_selector",
                        "status": "forbidden",
                        "message": f"你还未学过该标签: {element_tag}"
                    }
            except Exception as e:
                db.rollback()
                return {
                    "module": "element_selector",
                    "status": "error",
                    "error": str(e)
                }
        # 生成唯一ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        element_id = f"element_{timestamp}"
        # 保存到JSON文件
        filename = os.path.join(ELEMENTS_DIR, f"{element_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存元素信息: {element_id}")
        # 原有返回（注释掉）
        # return {
        #     "module": "element_selector",
        #     "status": "success",
        #     "element_id": element_id,
        #     "message": "元素信息已成功接收"
        # }
        # 新增：直接返回本次元素详细内容
        return {
            "module": "element_selector",
            "status": "success",
            "element_id": element_id,
            "element": {
                "id": element_id,
                **data
            },
            "message": "元素信息已成功接收"
        }
    except Exception as e:
        logger.error(f"处理元素信息时出错: {str(e)}")
        return {
            "module": "element_selector",
            "status": "error",
            "error": str(e)
        }

# 新增：获取单个元素信息
async def get_by_id_handler(element_id: str) -> Dict[str, Any]:
    try:
        filename = os.path.join(ELEMENTS_DIR, f"{element_id}.json")
        if not os.path.exists(filename):
            return {
                "module": "element_selector",
                "status": "error",
                "error": f"未找到ID为 {element_id} 的元素"
            }
        with open(filename, 'r', encoding='utf-8') as f:
            element_data = json.load(f)
        return {
            "module": "element_selector",
            "status": "success",
            "data": {"id": element_id, **element_data}
        }
    except Exception as e:
        logger.error(f"获取元素信息时出错: {str(e)}")
        return {
            "module": "element_selector",
            "status": "error",
            "error": str(e)
        }

# 注册模块（支持单个元素详情）
def register_element_selector(router):
    register_module("element_selector", get_handler, post_handler)
    # 额外注册单个元素详情接口
    if hasattr(router, 'add_api_route'):
        router.add_api_route(
            "/api/module/element_selector/{element_id}",
            get_by_id_handler,
            methods=["GET"],
            response_model=Dict[str, Any]
        )

# 兼容原有注册方式
try:
    from ..api import router
    register_element_selector(router)
except Exception:
    register_module("element_selector", get_handler, post_handler) 