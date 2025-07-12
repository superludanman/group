FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

# 安全配置
# 降低权限，使用非root用户运行
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# 限制资源使用
ENV MAX_WORKERS=1
ENV TIMEOUT=30