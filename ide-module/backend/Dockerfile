FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 添加必要的工具
RUN apt-get update && apt-get install -y \
    procps \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户运行应用
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/workdir \
    && chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 设置环境变量
ENV MAX_WORKERS=1
ENV TIMEOUT=30
ENV PORT=8080
ENV MAX_MEMORY=128m
ENV MAX_CPU=0.5

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# 设置标签
LABEL maintainer="AI HTML Learning Platform Team" \
      version="1.0" \
      description="Sandbox environment for running HTML/CSS/JS code safely"