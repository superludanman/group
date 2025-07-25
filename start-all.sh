#!/bin/bash

# 启动AI HTML学习平台的所有服务

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "启动AI HTML学习平台..."

# 加载根目录的环境变量文件
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "加载环境变量文件: $SCRIPT_DIR/.env"
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

# 获取端口配置，默认值保持与之前一致
BACKEND_PORT=${BACKEND_PORT:-8000}
IDE_MODULE_PORT=${IDE_MODULE_PORT:-8080}
FRONTEND_PORT=${FRONTEND_PORT:-9000}

# 启动主后端服务
echo "启动主后端服务 (端口 $BACKEND_PORT)..."
cd "$SCRIPT_DIR/backend"
# 使用项目的Python虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "已激活虚拟环境"
else
    echo "警告：未找到虚拟环境，使用系统Python"
fi

# 导出环境变量给Python进程
export BACKEND_PORT=$BACKEND_PORT
export IDE_MODULE_PORT=$IDE_MODULE_PORT

# 在环境变量设置后启动Python进程
BACKEND_PORT=$BACKEND_PORT python run.py > "$SCRIPT_DIR/main_backend.log" 2>&1 &
MAIN_BACKEND_PID=$!
cd "$SCRIPT_DIR"

# 启动IDE模块服务（通过主后端服务提供）
echo "IDE模块服务将通过主后端服务提供 (端口 $BACKEND_PORT)..."
# 不再单独启动IDE模块服务

# 启动前端服务，使用Node.js的http-server
echo "启动前端服务 (端口 $FRONTEND_PORT)..."
cd "$SCRIPT_DIR/frontend"
# 如果未安装http-server，则安装它
if ! command -v http-server &> /dev/null
then
    echo "安装http-server..."
    npm install -g http-server
fi

# 启动HTTP服务器，代理API请求到后端服务
nohup http-server -p $FRONTEND_PORT --proxy http://localhost:$BACKEND_PORT > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo "所有服务已启动！"
echo "主后端服务 PID: $MAIN_BACKEND_PID (端口 $BACKEND_PORT)"
echo "前端服务 PID: $FRONTEND_PID (端口 $FRONTEND_PORT)"
echo ""
echo "访问地址：http://localhost:$FRONTEND_PORT"
echo "日志文件：main_backend.log, frontend.log"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户按Ctrl+C停止服务
trap "echo '正在停止服务...'; kill $MAIN_BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 保持脚本运行
while true; do
    sleep 1
done