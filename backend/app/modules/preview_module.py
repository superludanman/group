"""
预览模块

此模块处理AI HTML学习平台的预览功能。
它展示了完成的HTML组件的外观，然后教用户如何创建它。
"""

from typing import Dict, Any
from fastapi import Request
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 导入模块加载器
from app.modules.module_loader import register_module

# 示例HTML组件预览
PREVIEW_EXAMPLES = {
    "navigation": {
        "name": "导航栏",
        "html": """
        <nav class="navbar">
            <div class="logo">我的网站</div>
            <ul class="nav-links">
                <li><a href="#">首页</a></li>
                <li><a href="#">关于</a></li>
                <li><a href="#">服务</a></li>
                <li><a href="#">联系我们</a></li>
            </ul>
        </nav>
        """,
        "explanation": "这个导航栏使用flexbox进行布局，包括一个logo和链接。这是网页设计中常见的网站导航模式。"
    },
    "card": {
        "name": "产品卡片",
        "html": """
        <div class="product-card">
            <img src="https://via.placeholder.com/150" alt="产品图片">
            <h3>产品名称</h3>
            <p class="price">¥199.99</p>
            <p class="description">这是产品的简短描述。</p>
            <button class="buy-button">加入购物车</button>
        </div>
        """,
        "explanation": "这个产品卡片展示了带有图片、名称、价格、描述和操作按钮的销售项目。卡片是多功能的UI组件。"
    },
    "form": {
        "name": "联系表单",
        "html": """
        <form class="contact-form">
            <h2>联系我们</h2>
            <div class="form-group">
                <label for="name">姓名：</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">邮箱：</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="message">留言：</label>
                <textarea id="message" name="message" rows="4" required></textarea>
            </div>
            <button type="submit">发送留言</button>
        </form>
        """,
        "explanation": "这个联系表单使用适当的标签和输入验证收集用户信息。表单对于用户交互和数据收集至关重要。"
    }
}

async def get_handler() -> Dict[str, Any]:
    """
    处理对模块API端点的GET请求。
    
    返回:
        包含模块数据的字典
    """
    logger.info("预览模块GET处理程序被调用")
    
    return {
        "module": "preview_module",
        "status": "active",
        "data": {
            "examples": list(PREVIEW_EXAMPLES.keys()),
            "current_example": "navigation"
        }
    }

async def post_handler(request: Request) -> Dict[str, Any]:
    """
    处理对模块API端点的POST请求。
    
    参数:
        request: 包含客户端数据的FastAPI请求对象
        
    返回:
        包含响应数据的字典
    """
    logger.info("预览模块POST处理程序被调用")
    
    # 从请求获取JSON数据
    data = await request.json()
    
    example_id = data.get("example_id", "navigation")
    action = data.get("action", "get_example")
    
    if action == "get_example" and example_id in PREVIEW_EXAMPLES:
        return {
            "module": "preview_module",
            "status": "success",
            "example": PREVIEW_EXAMPLES[example_id]
        }
    elif action == "next_example":
        # 获取列表中的下一个示例
        example_keys = list(PREVIEW_EXAMPLES.keys())
        current_index = example_keys.index(example_id) if example_id in example_keys else 0
        next_index = (current_index + 1) % len(example_keys)
        next_example_id = example_keys[next_index]
        
        return {
            "module": "preview_module",
            "status": "success",
            "example": PREVIEW_EXAMPLES[next_example_id],
            "example_id": next_example_id
        }
    else:
        return {
            "module": "preview_module",
            "status": "error",
            "message": f"未知操作或示例: {action}, {example_id}"
        }

# 向应用程序注册此模块
register_module("preview_module", get_handler, post_handler)