import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text

# 加载.env文件
load_dotenv()

# 从环境变量获取数据库配置，如果不存在则使用默认值
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "HTML_AI")

MYSQL_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

try:
    engine = create_engine(MYSQL_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("数据库连接成功，返回：", result.scalar())
except Exception as e:
    print("数据库连接失败：", e)