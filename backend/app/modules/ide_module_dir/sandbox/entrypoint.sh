#!/bin/bash
set -e

# 打印沙箱信息
echo "Starting code sandbox environment..."
echo "Workspace: /workspace"
echo "User: $(whoami)"

# 清理临时文件
cleanup() {
    echo "Cleaning up workspace..."
    rm -rf /workspace/temp/*
}

# 确保在容器停止时执行清理
trap cleanup EXIT

# 检查命令是否存在
if [ $# -eq 0 ]; then
    echo "No command provided, starting http-server..."
    exec http-server -p 3000
else
    echo "Executing command: $@"
    exec "$@"
fi