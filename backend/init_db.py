#!/usr/bin/env python3
"""
初始化数据库表
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from app.core.config import create_tables

if __name__ == "__main__":
    print("正在创建数据库表...")
    create_tables()
    print("数据库表创建完成！")