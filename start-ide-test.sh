#!/bin/bash

# 简化的启动脚本，用于快速测试IDE模块集成

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "启动AI HTML学习平台（简化版）..."

# 设置代理（如果需要）
# export https_proxy=http://127.0.0.1:7890

# 构建并启动Docker容器
echo "构建并启动Docker容器..."
if [ -d "$SCRIPT_DIR/backend/app/modules/ide_module_dir" ]; then
    cd "$SCRIPT_DIR/backend/app/modules/ide_module_dir"
    if [ -f "docker-compose.yml" ]; then
        # 检查环境变量文件是否存在，如果不存在则从示例创建
        if [ ! -f ".env" ] && [ -f ".env.example" ]; then
            echo "从.env.example创建.env文件..."
            cp .env.example .env
        fi
        
        # 加载环境变量
        if [ -f ".env" ]; then
            export $(grep -v '^#' .env | xargs)
        fi
        
        # 设置代理（如果环境变量中定义了代理）
        if [ -n "$HTTPS_PROXY" ]; then
            echo "设置HTTPS代理: $HTTPS_PROXY"
            export https_proxy=$HTTPS_PROXY
        fi
        
        if [ -n "$HTTP_PROXY" ]; then
            echo "设置HTTP代理: $HTTP_PROXY"
            export http_proxy=$HTTP_PROXY
        fi
        
        # 检查沙箱镜像是否存在
        if ! docker images | grep -q ${SANDBOX_IMAGE:-ide-sandbox:latest}; then
            echo "构建沙箱镜像..."
            cd sandbox
            if docker build -t ${SANDBOX_IMAGE:-ide-sandbox:latest} -f Dockerfile.sandbox .; then
                echo "沙箱镜像构建成功"
            else
                echo "沙箱镜像构建失败"
                cd ..
                cd "$SCRIPT_DIR"
                exit 1
            fi
            cd ..
        else
            echo "沙箱镜像已存在，跳过构建。"
        fi
        
        # 启动Docker容器
        echo "启动Docker容器..."
        if docker-compose up -d; then
            echo "Docker容器启动成功"
        else
            echo "Docker容器启动失败"
            cd "$SCRIPT_DIR"
            exit 1
        fi
    else
        echo "警告：未找到docker-compose.yml文件，跳过Docker容器启动"
    fi
    cd "$SCRIPT_DIR"
else
    echo "警告：未找到IDE模块目录，跳过Docker容器启动"
fi

# 启动主后端服务 (8000端口)
echo "启动主后端服务 (端口 8000)..."
cd "$SCRIPT_DIR/backend"
# 使用项目的Python虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "已激活虚拟环境"
else
    echo "警告：未找到虚拟环境，使用系统Python"
fi

if python run.py; then
    echo "后端服务启动成功"
else
    echo "后端服务启动失败"
fi

cd "$SCRIPT_DIR"