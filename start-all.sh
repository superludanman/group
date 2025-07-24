#!/bin/bash

# 启动AI HTML学习平台的所有服务

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "启动AI HTML学习平台..."

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
echo "按 Ctrl+C 停止服务"

# 等待用户按Ctrl+C停止服务
trap "echo '正在停止服务...'; kill $MAIN_BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 保持脚本运行
while true; do
    sleep 1
done