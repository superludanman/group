#!/bin/bash

# 启动AI HTML学习平台的所有服务

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "启动AI HTML学习平台..."

# 构建并启动Docker容器
echo "构建并启动Docker容器..."
if [ -d "$SCRIPT_DIR/backend/app/modules/ide_module_dir" ]; then
    cd "$SCRIPT_DIR/backend/app/modules/ide_module_dir"
    if [ -f "docker-compose.yml" ]; then
        # 检查环境变量文件是否存在，如果不存在则从示例创建
        if [ ! -f ".env" ]; then
            if [ -f ".env.example" ]; then
                echo "从.env.example创建.env文件..."
                cp .env.example .env
            else
                echo "警告：未找到.env或.env.example文件。"
            fi
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
        
        # 检查沙箱镜像是否存在，如果不存在则构建
        if ! docker images | grep -q ${SANDBOX_IMAGE:-ide-sandbox:latest}; then
            echo "构建沙箱镜像..."
            cd sandbox
            # 尝试构建，如果失败则显示错误信息
            if ! docker build -t ${SANDBOX_IMAGE:-ide-sandbox:latest} -f Dockerfile.sandbox .; then
                echo "警告：构建沙箱镜像失败。请检查网络连接和Docker配置。"
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
        if ! docker-compose up -d; then
            echo "警告：启动Docker容器失败。"
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

nohup python run.py > "$SCRIPT_DIR/main_backend.log" 2>&1 &
MAIN_BACKEND_PID=$!
cd "$SCRIPT_DIR"

# 启动前端服务 (9000端口)，使用Node.js的http-server
echo "启动前端服务 (端口 9000)..."
cd "$SCRIPT_DIR/frontend"
# 如果未安装http-server，则安装它
if ! command -v http-server &> /dev/null
then
    echo "安装http-server..."
    npm install -g http-server
fi

# 启动HTTP服务器，代理API请求到后端服务
nohup http-server -p 9000 --proxy http://localhost:8000 > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo "所有服务已启动！"
echo "主后端服务 PID: $MAIN_BACKEND_PID (端口 8000)"
echo "前端服务 PID: $FRONTEND_PID (端口 9000)"
echo ""
echo "访问地址：http://localhost:9000"
echo "日志文件：main_backend.log, frontend.log"
echo ""
echo "注意："
echo "1. 请确保已设置Docker环境并构建了ide-sandbox镜像"
echo "2. 如果遇到Docker连接问题，请设置代理：export https_proxy=http://127.0.0.1:7890"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户按Ctrl+C停止服务
trap "echo '正在停止服务...'; kill $MAIN_BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 保持脚本运行
while true; do
    sleep 1
done

echo "所有服务已启动！"
echo "主后端服务 PID: $MAIN_BACKEND_PID (端口 8000)"
echo "前端服务 PID: $FRONTEND_PID (端口 9000)"
echo ""
echo "访问地址：http://localhost:9000"
echo "日志文件：main_backend.log, frontend.log"
echo ""
echo "注意："
echo "1. 请确保已设置Docker环境并构建了ide-sandbox镜像"
echo "2. 如果遇到Docker连接问题，请设置代理：export https_proxy=http://127.0.0.1:7890"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户按Ctrl+C停止服务
trap "echo '正在停止服务...'; kill $MAIN_BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 保持脚本运行
while true; do
    sleep 1
done