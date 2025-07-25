from typing import Dict, Any
from fastapi import Request, Depends
import json
import os
import logging

from app.modules.module_loader import register_module
from app.core.models import Tag, UserTime
from app.core.config import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# 假设 catalog.json 路径
CATALOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Doc_Module/catalog.json'))

async def get_handler() -> Dict[str, Any]:
    """返回知识点目录和内容"""
    try:
        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        return {
            "module": "docs_module",
            "status": "active",
            "data": {
                "catalog": catalog
            }
        }
    except Exception as e:
        logger.error(f"加载知识点目录失败: {e}")
        return {
            "module": "docs_module",
            "status": "error",
            "error": str(e)
        }

async def post_handler(request: Request, db: Session = Depends(get_db)) -> dict:
    data = await request.json()
    action = data.get("action")
    if action == "record_time":
        base_time = int(data.get("base_time", 0))
        advanced_time = int(data.get("advanced_time", 0))
        try:
            user_time = db.query(UserTime).first()
            if user_time:
                user_time.base_time += base_time
                user_time.advanced_time += advanced_time
            else:
                user_time = UserTime(base_time=base_time, advanced_time=advanced_time)
                db.add(user_time)
            db.commit()
            return {"status": "success", "message": "记录成功"}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": f"数据库写入失败: {str(e)}"}
    tag_name = data.get("tag_name")
    if not tag_name:
        return {"status": "error", "message": "缺少 tag_name"}
    try:
        tag_data = {}
        for level in ['basic', 'intermediate', 'advanced', 'expert']:
            tag = db.query(Tag).filter_by(tag_name=tag_name, level=level).first()
            if tag:
                tag_data[level] = tag.description
        if not tag_data:
            return {"status": "error", "message": f"未找到标签 {tag_name} 的内容"}
        return {
            "module": "docs_module",
            "status": "success",
            "data": {
                "tag_name": tag_name,
                "contents": tag_data
            }
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"后端异常: {str(e)}"}

register_module("docs_module", get_handler, post_handler) 