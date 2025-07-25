from sqlalchemy import create_engine
from sqlalchemy import text

# 替换为你的实际数据库连接信息
MYSQL_URL = "mysql+pymysql://root:Yjd9854234@localhost:3306/HTML_AI?charset=utf8mb4"

try:
    engine = create_engine(MYSQL_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("数据库连接成功，返回：", result.scalar())
except Exception as e:
    print("数据库连接失败：", e)